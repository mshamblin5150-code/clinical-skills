"""Cover ``research_ledger``'s parser and rows against synthetic ledgers.

Every ledger here is written in this file and a temp directory, the way
``test_skills_mirror`` builds throwaway checkouts rather than touching the real
one. **There is no committed research ledger and there will not be one**: a ledger
lives under ``scratch/`` because its claims are transcribed from faculty material
about a patient, which is the same reason ``test_differential_scan`` has no run to
point at.

``TheSkillSaysWhatThisChecks`` is the one class that reads a committed file, and it
is here for ``test_spelling_scan``'s reason: a scanner that has drifted from the
file a reader opens is worse than no scanner, because it reads as agreement. **It
runs the scanner over the skill's own worked example** rather than only matching
strings -- a documented record shape the grader would refuse is the drift this
class exists to catch, and it is the form of it a substring test cannot see.

**The vocabularies are imported, never retyped.** A list copied into a test goes
stale the first time the module's own changes and reads as coverage while it does,
which is ``test_build_artifacts_ignored``'s finding.
"""

from __future__ import annotations

import ast
import inspect
import io
import re
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

import checks_ledger
import docx_write
import reference_scan
import research_ledger as ledger
import coursework_run
from grader_conformance import constructed_kinds, for_module
from prose_bind import ProseBind, normalized as normalized_prose

GraderConformance = for_module(ledger)
import run_grader

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"
STYLE = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "style.md"

AS_OF = date(2026, 8, 19)

# A record that passes every row, so a test can change one field and know the
# finding it gets back belongs to that field.
CLEAN = """\
## CLAIM: A white count of 15,000 is within physiologic leukocytosis in pregnancy.
STATUS: sourced
SOURCE: peer-reviewed
REFERENCE: Abbassi-Ghanavati, M. (2009). Pregnancy and laboratory studies.
    Obstetrics and Gynecology, 114(6), 1326-1331.
RESTATEMENT: The table gives a third-trimester white cell range of 5.6 to
    16.9 x 10^9/L in normal pregnancy.
RECENCY: nothing newer - searched 2026-08-19, no later reference-range table exists.
RESOLVED: https://doi.org/10.1097/AOG.0b013e3181c2bde8 - read 2026-08-19
PAGE-YEAR: 2009 - stated on the article's masthead and in the journal citation.
REFUTATION: stands - the volume, issue and pages match the publisher's landing
    page, and the third-trimester row is on page 1327.
SECOND-ROUTE: publisher HTML -> journal PDF rendered at 600 dpi
STATED-EXPIRY: none stated
"""


def ledger_text(*records: str, stamp: str = "2026-08-19") -> str:
    """A whole ledger: the date header, then the records."""
    header = f"DATE: {stamp}\n\n" if stamp else ""
    return header + "\n".join(records)


def kinds(text: str, as_of: date | None = AS_OF) -> list[str]:
    """The finding kinds one ledger produces, in order."""
    records = ledger.read_records(text)
    return [f.kind for record in records for f in ledger.record_findings(record, as_of)]


def replace_field(record: str, name: str, value: str | None) -> str:
    """Rewrite one field of a record, or drop it when ``value`` is ``None``.

    Wrapped continuations of the field go with it, which is what makes this safe
    to use on ``CLEAN`` -- two of its fields wrap.
    """
    out: list[str] = []
    skipping = False
    for line in record.splitlines():
        named = ledger.FIELD.match(line)
        if named:
            skipping = named.group(1).upper() == name
            if skipping:
                if value is not None:
                    out.append(f"{name}: {value}")
                continue
        elif skipping and not ledger.CLAIM.match(line) and line.strip():
            continue
        else:
            skipping = False
        out.append(line)
    return "\n".join(out) + "\n"


def with_reference(record: str, reference: str) -> str:
    """Set the reference and move ``PAGE-YEAR`` with it.

    **#231 coupled the two**: the year on the page has to agree with the year in
    the entry, so a fixture that ages one and leaves the other reports a
    disagreement rather than the row it meant to test. Every fixture below that
    changes a reference year goes through here, which is why none of them has to
    know the coupling exists.
    """
    match = ledger.YEAR.search(reference)
    page = f"{match.group(1)} - stated on the masthead." if match else "the page states no year."
    return replace_field(replace_field(record, "REFERENCE", reference), "PAGE-YEAR", page)


def vocabularies_keyword_of_serves() -> dict[str, tuple[str, ...]]:
    """Every vocabulary the module actually hands ``keyword_of``, read off its own
    source by AST rather than typed here.

    A list typed into a test goes stale the first time the module's own moves and
    reads as coverage while it does, which is ``test_build_artifacts_ignored``'s
    finding and this file's own opening rule. A fourth vocabulary would otherwise
    leave the boundary loops below green while covering three of four -- the
    passes-for-the-wrong-reason case, on ``test_console_codec``'s instrument and
    for its reason: a substring search would have matched the ``def`` line and the
    docstring, neither of which is a call.
    """
    tree = ast.parse(Path(ledger.__file__).read_text(encoding="utf-8"))
    served: dict[str, tuple[str, ...]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        named = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        if named != "keyword_of" or len(node.args) < 2:
            continue
        second = node.args[1]
        if isinstance(second, ast.Name):
            served[second.id] = getattr(ledger, second.id)
    return served


class TheParserReadsARecordAndItsWrappedFields(unittest.TestCase):
    def test_a_record_opens_on_a_claim_heading(self):
        records = ledger.read_records(ledger_text(CLEAN))
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0].claim.startswith("A white count of 15,000"))

    def test_the_date_header_is_not_a_record(self):
        """It sits above the first claim, so nothing owns it."""
        self.assertEqual(ledger.read_records("DATE: 2026-08-19\nSTATUS: sourced\n"), [])

    def test_a_field_value_runs_to_the_next_field(self):
        """An APA entry wraps onto a hanging indent, and has to survive it."""
        record = ledger.read_records(ledger_text(CLEAN))[0]
        self.assertIn("Obstetrics and Gynecology, 114(6), 1326-1331.", record.value("REFERENCE"))
        self.assertNotIn("RESTATEMENT", record.value("REFERENCE"))

    def test_the_heading_level_is_free(self):
        """So a ledger can sit under a document heading without the parser caring."""
        deeper = ledger_text(CLEAN.replace("## CLAIM:", "#### CLAIM:", 1))
        self.assertEqual(len(ledger.read_records(deeper)), 1)

    def test_two_records_do_not_bleed_into_each_other(self):
        second = CLEAN.replace("A white count", "A different claim")
        records = ledger.read_records(ledger_text(CLEAN, second))
        self.assertEqual(len(records), 2)
        self.assertTrue(records[1].claim.startswith("A different claim"))

    def test_the_clean_record_fails_nothing(self):
        self.assertEqual(kinds(ledger_text(CLEAN)), [])


class DeclaredLimitsHaveDurableNames(unittest.TestCase):
    """ADR 0053 ruling 8's public object and derived sentence view."""

    def test_each_row_is_key_sentence_and_evidence_disposition(self):
        for row in ledger.DECLARED_LIMITS:
            with self.subTest(key=row.key):
                self.assertIsInstance(row, ledger.DeclaredLimit)
                self.assertTrue(row.key.strip())
                self.assertTrue(row.limit.strip())
                self.assertIsInstance(row.evidence, ledger.EvidenceDisposition)

    def test_not_reached_is_the_order_preserving_sentence_view(self):
        self.assertEqual(
            ledger.NOT_REACHED,
            tuple(row.limit for row in ledger.DECLARED_LIMITS),
        )

    def test_keys_are_distinct(self):
        keys = [row.key for row in ledger.DECLARED_LIMITS]
        self.assertEqual(len(keys), len(set(keys)))

    def test_the_object_is_live(self):
        self.assertTrue(ledger.DECLARED_LIMITS)

    def test_authenticated_research_route_limit_names_both_unobservable_steps(self):
        limits = {row.key: row for row in ledger.DECLARED_LIMITS}
        row = limits["research-authenticated-route-unverified"]
        self.assertEqual(
            row.limit,
            "Nothing can see whether the browser was opened, and nothing can see "
            "whether the profile's answer was consulted.",
        )
        self.assertIs(row.evidence, ledger.EvidenceDisposition.DECLARED_READING)

    def test_declared_limits_do_not_print(self):
        report = ledger.format_report(
            ledger.survey(ledger.read_records(CLEAN), AS_OF), "claims.md"
        )
        for row in ledger.DECLARED_LIMITS:
            with self.subTest(key=row.key):
                self.assertNotIn(row.key, report)
                self.assertNotIn(row.limit, report)


def module_prose_without_inventory() -> str:
    """The module surface with the canonical rows themselves removed."""

    source = Path(ledger.__file__).read_text(encoding="utf-8")
    start = source.index("DECLARED_LIMITS =")
    end = source.index("NOT_REACHED =", start)
    return source[:start] + source[end:]


def ledger_publishing_skills(read_text=None) -> tuple[Path, ...]:
    """Derive publishing skills from their literal ledger-template marker.

    This predicate can see only the literal ``## CLAIM:`` spelling: a skill that
    publishes a ledger through another template spelling is outside its ceiling.
    """
    reader = read_text or (lambda path: path.read_text(encoding="utf-8"))
    return tuple(
        path
        for path in sorted((REPO_ROOT / "skills").glob("*/SKILL.md"))
        if "## CLAIM:" in reader(path)
    )


def authenticated_research_route_blocks(path: Path, read_text=None) -> tuple[str, ...]:
    """Normalized prose blocks carrying the research-side route obligation.

    This recognizes only one blank-line-delimited block carrying the literal
    concept vocabulary below. A paraphrase outside those regex forms is beyond
    its ceiling and is not evidence that the obligation is absent.
    """

    required = (
        r"\bprofile\b",
        r"\bavailable\b",
        r"\bresearch(?:er| agent| context)\b",
        r"\bauthenticated route\b",
        r"\bmust\b",
        r"\bbefore\b.*\bgiv(?:e|ing) up\b",
        r"\bsubstitut(?:e|ion)\b",
        r"\bstatus\s*:\s*unsourced\b",
    )
    reader = read_text or (lambda source: source.read_text(encoding="utf-8"))
    blocks = (
        normalized_prose(block)
        for block in re.split(r"\n\s*\n", reader(path))
    )
    return tuple(
        block
        for block in blocks
        if all(re.search(pattern, block, re.IGNORECASE) for pattern in required)
    )


def claim_blocks(path: Path) -> tuple[str, ...]:
    """Fenced templates and examples that actually publish claim records."""
    blocks: list[str] = []
    current: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            if current is None:
                current = []
            else:
                block = "\n".join(current) + "\n"
                if ledger.CLAIM.search(block):
                    blocks.append(block)
                current = None
            continue
        if current is not None:
            current.append(line)
    return tuple(blocks)


class EveryLedgerPublishingSkillCarriesTheRecordContract(unittest.TestCase):
    """#498 and #500's one shared, derived-population vocabulary bind."""

    def test_every_publishing_skill_names_every_required_field(self):
        for path in ledger_publishing_skills():
            blocks = claim_blocks(path)
            self.assertTrue(blocks, path.parent.name)
            for block in blocks:
                for name in ledger.REQUIRED_WHEN_SOURCED:
                    with self.subTest(skill=path.parent.name, field=name):
                        self.assertIn(f"{name}:", block)

    def test_every_publishing_skill_carries_both_new_field_vocabularies(self):
        for path in ledger_publishing_skills():
            for block in claim_blocks(path):
                with self.subTest(skill=path.parent.name):
                    self.assertIn("none stated", block)
                    self.assertIn("SECOND-ROUTE", block)
                    self.assertIn("->", block)
                    if "<" in block:
                        self.assertIn("superseded cited deliberately", block)

    def test_every_concrete_worked_example_passes_the_scanner(self):
        examples = [
            block
            for path in ledger_publishing_skills()
            for block in claim_blocks(path)
            if "<" not in block
        ]
        self.assertTrue(examples)
        for example in examples:
            records = ledger.read_records(example)
            self.assertTrue(records)
            stamp = ledger.DATE_HEADER.search(example)
            self.assertIsNotNone(stamp)
            as_of = date(int(stamp.group(1)), int(stamp.group(2)), int(stamp.group(3)))
            for record in records:
                self.assertEqual(ledger.record_findings(record, as_of), [])

    def test_the_population_changes_when_a_claim_marker_is_removed(self):
        baseline = ledger_publishing_skills()
        self.assertTrue(baseline)
        target = baseline[0]

        def without_target_marker(path: Path) -> str:
            text = path.read_text(encoding="utf-8")
            if path == target:
                return text.replace("## CLAIM:", "## RESEARCH CLAIM:")
            return text

        mutated = ledger_publishing_skills(without_target_marker)
        self.assertNotIn(target, mutated)
        self.assertEqual(set(mutated), set(baseline) - {target})


class EveryLedgerPublishingSkillCarriesTheAuthenticatedResearchRoute(unittest.TestCase):
    """ADR 0055 rulings 2, 5, and 6, over the derived skill population."""

    def test_each_research_brief_carries_the_conditional_route_obligation(self):
        for path in ledger_publishing_skills():
            with self.subTest(skill=path.parent.name):
                self.assertTrue(authenticated_research_route_blocks(path), path)

    def test_removing_one_required_concept_makes_a_real_skill_unrecognized(self):
        target = ledger_publishing_skills()[0]

        def without_giving_up(path: Path) -> str:
            prose = path.read_text(encoding="utf-8")
            if path == target:
                prose = re.sub(r"\bgiv(?:e|ing) up\b", "stopping", prose, count=1)
            return prose

        self.assertTrue(authenticated_research_route_blocks(target))
        self.assertFalse(
            authenticated_research_route_blocks(target, without_giving_up)
        )


class DeclaredLimitProsePointsWithoutCopying(ProseBind, unittest.TestCase):
    """ADR 0053 ruling 10's two-direction, live, mutation-tested bind."""

    SHINGLE = 8
    SURFACES = {
        "the module prose": module_prose_without_inventory,
        "CLAUDE.md": lambda: (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8"),
        "discussion-post": lambda: (
            REPO_ROOT / "skills" / "discussion-post" / "SKILL.md"
        ).read_text(encoding="utf-8"),
        "discussion-reply": lambda: (
            REPO_ROOT / "skills" / "discussion-reply" / "SKILL.md"
        ).read_text(encoding="utf-8"),
        "practicum-case-study": lambda: SKILL.read_text(encoding="utf-8"),
    }

    @classmethod
    def shingles(cls, text: str) -> set[str]:
        words = normalized_prose(text).split()
        return {
            " ".join(words[index : index + cls.SHINGLE])
            for index in range(len(words) - cls.SHINGLE + 1)
        }

    @classmethod
    def copies_in(cls, text: str) -> list[str]:
        normalized = normalized_prose(text)
        prose = cls.shingles(normalized)
        found = []
        for row in ledger.DECLARED_LIMITS:
            if row.key in normalized:
                found.append(f"{row.key}: names the key")
            shared = sorted(cls.shingles(row.limit) & prose)
            if shared:
                found.append(f"{row.key}: {shared[0]!r}")
        return found

    def test_every_surface_points_at_the_object_and_copies_no_row(self):
        for where, read in self.SURFACES.items():
            with self.subTest(where=where):
                prose = read()
                self.assertProseIn("research_ledger.DECLARED_LIMITS", prose)
                self.assertEqual(self.copies_in(prose), [], where)

    def test_the_bind_is_live_in_both_directions(self):
        self.assertTrue(ledger.DECLARED_LIMITS)
        for where, read in self.SURFACES.items():
            with self.subTest(where=where):
                self.assertGreater(len(read()), 200)

    def test_a_planted_key_and_sentence_each_trigger_the_copy_detector(self):
        for row in ledger.DECLARED_LIMITS:
            with self.subTest(key=row.key):
                self.assertTrue(self.copies_in(f"See the object. {row.key}."))
                self.assertTrue(self.copies_in(f"See the object. {row.limit}"))
        self.assertEqual(
            self.copies_in("See research_ledger.DECLARED_LIMITS for the limits."),
            [],
        )


class EveryBehaviorLimitHasALiveHandler(unittest.TestCase):
    """Bind each behavior row to its blind-spot test and positive control."""

    HANDLERS = {
        "record-population-unbounded": ("AHeadingWhoseAnswerNeverArrivedIsAFinding.test_a_short_ledger_is_only_visible_because_the_headings_were_written_first", "AHeadingWhoseAnswerNeverArrivedIsAFinding.test_a_bare_heading_fails"),
        "restatement-semantic-equivalence-unchecked": ("TheRestatementIsNotTheClaimAgain.test_a_real_paraphrase_passes", "TheRestatementIsNotTheClaimAgain.test_pasting_the_claim_back_is_a_finding"),
        "numeric-values-uncompared": ("ANumericClaimGetsANumericRestatement.test_the_source_may_answer_in_its_own_units", "ANumericClaimGetsANumericRestatement.test_a_number_answered_with_prose_is_a_finding"),
        "two-year-target-unenforced": ("TheRecencyRuleIsTheAmendedOne.test_the_window_boundary_is_five_years_inclusive", "TheRecencyRuleIsTheAmendedOne.test_an_old_source_with_no_excuse_is_a_finding"),
        "doi-shape-overmatches": ("TheDoiBranchOfTheLocatorMatchesAPageRange.test_a_page_range_shaped_like_a_doi_matches", "TheDoiBranchOfTheLocatorMatchesAPageRange.test_prose_with_no_locator_shape_still_fails_the_row"),
        "read-date-lower-bound-absent": ("DeclaredLimitBehaviorControls.test_a_read_date_long_before_the_ledger_passes", "DeclaredLimitBehaviorControls.test_a_read_date_after_the_ledger_fires"),
        "paywall-body-unread": ("TheRefutationPassIsASecondAgentTryingToProveTheCitationWrong.test_a_paywall_passes_because_the_wall_is_not_an_absence", "TheRefutationPassIsASecondAgentTryingToProveTheCitationWrong.test_a_refuted_citation_is_a_failure_and_not_an_outcome"),
        "page-year-first-plausible-token": ("ThePageYearIsCheckedAgainstTheEntry.test_a_page_number_that_is_itself_a_plausible_year_still_wins", "ThePageYearIsCheckedAgainstTheEntry.test_a_page_number_before_the_year_is_not_read_as_the_year"),
        "prescription-number-correctness-unchecked": ("AClaimForADosedDrugCarriesTheNumber.test_the_row_never_compares_the_numbers", "AClaimForADosedDrugCarriesTheNumber.test_a_dosed_row_answered_by_a_claim_with_no_number"),
        "dose-claim-accepts-any-number": ("TheDoseRowAsksForANumberAndNotForTheNumber.test_a_year_in_the_heading_satisfies_the_row", "AClaimForADosedDrugCarriesTheNumber.test_a_dosed_row_answered_by_a_claim_with_no_number"),
        "welded-drug-hidden": ("OneDrugRowIsOneDrugAndNothingHereMakesThatTrue.test_the_second_drugs_dose_is_graded_by_nothing", "EveryPrescribedDrugHasAClaimRecord.test_a_drug_no_record_names_is_the_ticket_itself"),
        "leading-token-drug-parser": ("ADrugRowIsReadOffTheDispSigPair.test_the_drug_is_the_leading_token_and_the_rest_is_the_order", "EveryPrescribedDrugHasAClaimRecord.test_an_unreadable_drug_row_is_a_finding_and_not_a_silent_drop"),
        "spelled-dose-unseen": ("ADrugRowIsReadOffTheDispSigPair.test_a_row_with_no_digit_states_no_dose", "AClaimForADosedDrugCarriesTheNumber.test_a_dosed_row_answered_by_a_claim_with_no_number"),
        "dose-versus-indication-unseen": ("DeclaredLimitBehaviorControls.test_an_indication_number_satisfies_the_dose_row", "DeclaredLimitBehaviorControls.test_the_same_indication_without_a_number_fires"),
        "drug-sig-agreement-unseen": ("DeclaredLimitBehaviorControls.test_a_conflicting_sig_does_not_change_the_parsed_order", "ADrugRowIsReadOffTheDispSigPair.test_a_table_carrying_disp_and_no_sig_is_not_a_prescription"),
        "table-record-number-equivalence-unseen": ("AClaimForADosedDrugCarriesTheNumber.test_the_row_never_compares_the_numbers", "AClaimForADosedDrugCarriesTheNumber.test_a_dosed_row_answered_by_a_claim_with_no_number"),
        "partial-prescription-table-nonfatal": ("TheDraftFlagIsGradedAndItsAbsenceIsDeclared.test_a_short_read_is_outside_the_exit_status_and_says_so", "TheDraftFlagIsGradedAndItsAbsenceIsDeclared.test_a_draft_with_no_prescription_table_exits_two"),
        "evidence-cross-references-ungraded": ("ACarriedTopicIsRecognizedByItsMasthead.test_a_cross_reference_is_not_a_body", "ACarriedTopicIsRecognizedByItsMasthead.test_a_body_is_carried"),
        "unmastheaded-evidence-body-unseen": ("DeclaredLimitBehaviorControls.test_an_unmastheaded_topic_body_is_not_carried", "ACarriedTopicIsRecognizedByItsMasthead.test_a_body_is_carried"),
        "non-uptodate-evidence-unjoined": ("ACitedTopicTheDumpDoesNotCarryIsRefused.test_a_journal_citation_is_left_alone", "ACitedTopicTheDumpDoesNotCarryIsRefused.test_an_uncarried_topic_is_a_finding"),
        "unrecognizable-uptodate-entry-unseen": ("DeclaredLimitBehaviorControls.test_an_entry_with_neither_database_nor_locator_is_unseen", "AnUpToDateEntryThisCannotReadIsAFinding.test_an_uptodate_locator_with_no_database_element_is_a_finding"),
        "uncited-missing-topic-unseen": ("DeclaredLimitBehaviorControls.test_a_missing_topic_with_no_citation_is_unseen", "ACitedTopicTheDumpDoesNotCarryIsRefused.test_an_uncarried_topic_is_a_finding"),
        "draft-rows-optional": ("TheDraftFlagIsGradedAndItsAbsenceIsDeclared.test_without_the_flag_the_three_rows_read_not_graded", "TheDraftFlagIsGradedAndItsAbsenceIsDeclared.test_with_the_flag_the_rows_carry_counts"),
        "evidence-rows-optional": ("TheEvidenceRowsAreWiredInLikeTheDraftRows.test_the_report_says_not_graded_without_the_flag", "TheEvidenceRowsAreWiredInLikeTheDraftRows.test_the_report_states_the_population_when_it_ran"),
        "evidence-without-draft-skips-references": ("DeclaredLimitBehaviorControls.test_evidence_without_draft_supplies_no_reference_entries", "DeclaredLimitBehaviorControls.test_evidence_with_draft_reads_reference_entries"),
        "reply-reference-label-unchecked": ("DeclaredLimitBehaviorControls.test_the_reply_path_accepts_a_misspelled_reference_label", "DeclaredLimitBehaviorControls.test_reference_scan_rejects_the_same_label"),
    }

    def test_behavior_keys_are_exactly_the_handled_keys(self):
        behavior = {
            row.key
            for row in ledger.DECLARED_LIMITS
            if row.evidence is ledger.EvidenceDisposition.BEHAVIOR
        }
        self.assertEqual(behavior, set(self.HANDLERS))

    def test_every_handler_runs_a_blind_spot_and_positive_control(self):
        for key, (blind_spot, positive_control) in self.HANDLERS.items():
            with self.subTest(key=key):
                self.assertNotEqual(blind_spot, positive_control)
                for named in (blind_spot, positive_control):
                    result = unittest.TestResult()
                    unittest.defaultTestLoader.loadTestsFromName(
                        f"test_research_ledger.{named}"
                    ).run(result)
                    self.assertTrue(
                        result.wasSuccessful(),
                        f"{key}: {named}: {result.errors + result.failures}",
                    )


class DeclaredLimitBehaviorControls(unittest.TestCase):
    """Direct controls for boundaries that do not have a natural row test."""

    def test_a_read_date_long_before_the_ledger_passes(self):
        record = replace_field(CLEAN, "RESOLVED", "https://example.test - read 2020-01-01")
        self.assertNotIn(ledger.READ_AFTER_DATE, kinds(ledger_text(record)))

    def test_a_read_date_after_the_ledger_fires(self):
        record = replace_field(CLEAN, "RESOLVED", "https://example.test - read 2027-01-01")
        self.assertIn(ledger.READ_AFTER_DATE, kinds(ledger_text(record)))

    def test_a_conflicting_sig_does_not_change_the_parsed_order(self):
        first = ledger.read_prescriptions(rx_table(CEFTRIAXONE, sig="Take for infection."))
        second = ledger.read_prescriptions(rx_table(CEFTRIAXONE, sig="Take for migraine."))
        self.assertEqual(first, second)

    def test_an_indication_number_satisfies_the_dose_row(self):
        claim = "Ceftriaxone is indicated for 2 clinical syndromes."
        self.assertEqual(rx_kinds(rx_table(CEFTRIAXONE), a_drug_claim(claim)), [])

    def test_the_same_indication_without_a_number_fires(self):
        claim = "Ceftriaxone is indicated for two clinical syndromes."
        self.assertEqual(
            rx_kinds(rx_table(CEFTRIAXONE), a_drug_claim(claim)),
            [ledger.DOSE_NOT_CLAIMED],
        )

    def test_an_unmastheaded_topic_body_is_not_carried(self):
        self.assertEqual(
            ledger.carried_topics("A topic title\nTreatment details without a masthead.\n"),
            set(),
        )

    def test_an_entry_with_neither_database_nor_locator_is_unseen(self):
        record = """\
## CLAIM: A claim resting on an unrecognizable entry.
STATUS: sourced
REFERENCE: Author, A. (2026). Some topic. Retrieved August 20, 2026.
"""
        found, read = ledger.evidence_findings(
            ledger.read_records(ledger_text(record)), (), {"Some topic"}
        )
        self.assertEqual((found, read), ([], 0))

    def test_a_missing_topic_with_no_citation_is_unseen(self):
        self.assertEqual(ledger.evidence_findings([], (), {"A carried topic"}), ([], 0))

    def test_evidence_without_draft_supplies_no_reference_entries(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            claims = root / "claims.md"
            evidence = root / "evidence.txt"
            claims.write_text(ledger_text(CLEAN), encoding="utf-8")
            evidence.write_text(topic("A carried topic"), encoding="utf-8")
            parsed = run_grader.Parsed(
                str(claims), values={"--evidence": str(evidence)}
            )
            with mock.patch.object(ledger, "read_document") as read_document:
                source = ledger._load(parsed)
        read_document.assert_not_called()
        self.assertEqual(source.entries, ())

    def test_evidence_with_draft_reads_reference_entries(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            claims = root / "claims.md"
            evidence = root / "evidence.txt"
            draft = root / "draft.md"
            claims.write_text(ledger_text(CLEAN), encoding="utf-8")
            evidence.write_text(topic("A carried topic"), encoding="utf-8")
            draft.write_text("## References\nAn entry.\n", encoding="utf-8")
            parsed = run_grader.Parsed(
                str(claims),
                values={"--evidence": str(evidence), "--draft": str(draft)},
            )
            parsed_document = mock.Mock(entries=(mock.Mock(text="An entry."),))
            with mock.patch.object(
                ledger, "read_document", return_value=parsed_document
            ) as read_document:
                source = ledger._load(parsed)
        read_document.assert_called_once()
        self.assertEqual(source.entries, ("An entry.",))

    def test_the_reply_path_accepts_a_misspelled_reference_label(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            claims = root / "claims.md"
            reply = root / "reply.md"
            claims.write_text(ledger_text(CLEAN), encoding="utf-8")
            reply.write_text("# Reply\n\n## Refrences\n\nAn entry.\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = ledger.main([str(claims)])
        self.assertEqual(status, 0)

    def test_reference_scan_rejects_the_same_label(self):
        with tempfile.TemporaryDirectory() as raw:
            reply = Path(raw) / "reply.md"
            reply.write_text("# Reply\n\n## Refrences\n\nAn entry.\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = reference_scan.main(
                    [str(reply), "--as-of", "2026-08-19"]
                )
        self.assertEqual(status, 2)
        self.assertIn("no reference list", out.getvalue() + err.getvalue())


class AStatusIsOneOfTwoBranches(unittest.TestCase):
    """An unrecognized status is a failure, and that departs from
    ``specificity_scan``'s third-branch rule on purpose.

    There the keyword picks a message. Here it picks **which tests run**, so a
    record reading ``STATUS: pending`` skips every row below it and prints as
    clean -- the silent-pass shape this whole directory exists for.
    """

    def test_a_third_word_is_a_finding(self):
        record = replace_field(CLEAN, "STATUS", "pending")
        self.assertIn(ledger.UNKNOWN_STATUS, kinds(ledger_text(record)))

    def test_a_third_word_does_not_also_report_the_rows_it_skipped(self):
        """One finding, not seven. A record graded on nothing has one defect."""
        record = replace_field(CLEAN, "STATUS", "pending")
        self.assertEqual(kinds(ledger_text(record)), [ledger.UNKNOWN_STATUS])

    def test_a_missing_status_is_the_same_finding(self):
        record = replace_field(CLEAN, "STATUS", None)
        self.assertEqual(kinds(ledger_text(record)), [ledger.UNKNOWN_STATUS])


class AHeadingWhoseAnswerNeverArrivedIsAFinding(unittest.TestCase):
    """#206's shared-artifact channel, with lost writes where that ticket has
    leaked reads.

    This tool has no expected record count, so three records where eight claims
    went out would grade clean and the run would draft.
    ``skills/practicum-case-study/SKILL.md`` step 3 closes that by writing the
    headings down **before** spawning anything and keeping one writer -- and then
    a lost answer is a heading with no ``STATUS``, which already fails. **The fix
    is an ordering rather than a row**, and this pins the consequence the
    ordering depends on.
    """

    def test_a_bare_heading_fails(self):
        text = ledger_text("## CLAIM: A claim whose agent never came back.\n")
        self.assertEqual(kinds(text), [ledger.UNKNOWN_STATUS])

    def test_a_short_ledger_is_only_visible_because_the_headings_were_written_first(self):
        """Three answered claims out of eight: clean if the five lost headings were
        never written, refused if they were."""
        answered = ledger_text(CLEAN, CLEAN, CLEAN)
        self.assertEqual(kinds(answered), [])
        with_headings = ledger_text(
            CLEAN, CLEAN, CLEAN, *[f"## CLAIM: Claim {n}.\n" for n in range(4, 9)]
        )
        self.assertEqual(kinds(with_headings), [ledger.UNKNOWN_STATUS] * 5)


class AnUnsourcedRecordSaysWhatWasSearched(unittest.TestCase):
    """The claim goes to ``PROPOSED``, so the record is not a failure -- but a
    bare keyword is the assertion without the looking."""

    def _record(self, status: str, reference: str | None = None) -> str:
        record = f"## CLAIM: Something nobody could source.\nSTATUS: {status}\n"
        if reference is not None:
            record += f"REFERENCE: {reference}\n"
        return record

    def test_an_unsourced_record_with_a_reason_fails_nothing(self):
        text = ledger_text(self._record("unsourced - searched PubMed, IDSA and UpToDate."))
        self.assertEqual(kinds(text), [])

    def test_a_bare_unsourced_is_a_finding(self):
        self.assertEqual(kinds(ledger_text(self._record("unsourced"))), [ledger.BARE_STATUS])

    def test_an_unsourced_record_may_not_carry_a_reference(self):
        """The two statements contradict, and nothing else can tell which was meant."""
        text = ledger_text(
            self._record("unsourced - nothing found.", "Someone, A. (2024). A thing. Journal.")
        )
        self.assertEqual(kinds(text), [ledger.UNSOURCED_WITH_CITATION_FIELD])

    def test_an_unsourced_record_is_counted_so_the_run_knows(self):
        text = ledger_text(self._record("unsourced - searched three databases."))
        scan = ledger.survey(ledger.read_records(text), AS_OF)
        self.assertEqual((scan.unsourced, scan.failing_records), (1, 0))


class ARequiredFieldIsPresentAndCarriesSomething(unittest.TestCase):
    def test_every_sourced_field_is_required(self):
        for name in ledger.REQUIRED_WHEN_SOURCED:
            with self.subTest(field=name):
                self.assertIn(ledger.MISSING_FIELD, kinds(ledger_text(replace_field(CLEAN, name, None))))

    def test_a_field_present_but_empty_is_the_same_defect(self):
        record = replace_field(CLEAN, "RESTATEMENT", "")
        self.assertIn(ledger.MISSING_FIELD, kinds(ledger_text(record)))

    def test_a_claim_heading_with_no_claim_is_a_finding(self):
        record = CLEAN.replace(
            "## CLAIM: A white count of 15,000 is within physiologic leukocytosis in pregnancy.",
            "## CLAIM:",
            1,
        )
        self.assertIn(ledger.MISSING_FIELD, kinds(ledger_text(record)))


class TheSourceClassComesFromTheVocabulary(unittest.TestCase):
    """A fixed vocabulary is ``threshold_sheet``'s population key for its reason:
    a machine can only compare strings, and a mis-keyed value is a wrong *word* a
    reader can see rather than a silent miss."""

    def test_every_declared_class_passes(self):
        for name in ledger.SOURCE_CLASSES:
            with self.subTest(source=name):
                self.assertEqual(kinds(ledger_text(replace_field(CLEAN, "SOURCE", name))), [])

    def test_a_content_farm_is_outside_it(self):
        record = replace_field(CLEAN, "SOURCE", "a blog post")
        self.assertIn(ledger.UNKNOWN_SOURCE_CLASS, kinds(ledger_text(record)))

    def test_the_match_ignores_case_and_punctuation(self):
        record = replace_field(CLEAN, "SOURCE", "Peer Reviewed")
        self.assertEqual(kinds(ledger_text(record)), [])


class TheRestatementIsNotTheClaimAgain(unittest.TestCase):
    """The cheap half of the limb #214 calls the one that matters most."""

    def test_pasting_the_claim_back_is_a_finding(self):
        claim = "A white count of 15,000 is within physiologic leukocytosis in pregnancy."
        record = replace_field(CLEAN, "RESTATEMENT", claim)
        self.assertIn(ledger.RESTATEMENT_ECHOES_CLAIM, kinds(ledger_text(record)))

    def test_repunctuating_the_claim_is_still_the_claim(self):
        record = replace_field(
            CLEAN,
            "RESTATEMENT",
            "A white count of 15,000, is within physiologic leukocytosis in pregnancy",
        )
        self.assertIn(ledger.RESTATEMENT_ECHOES_CLAIM, kinds(ledger_text(record)))

    def test_a_real_paraphrase_passes(self):
        self.assertEqual(kinds(ledger_text(CLEAN)), [])

    def test_equality_only_and_never_similarity(self):
        """Anything looser would be a guess about paraphrase, and paraphrase is
        the whole point of the field."""
        record = replace_field(
            CLEAN,
            "RESTATEMENT",
            "A white count of 15,000 is within physiologic leukocytosis in pregnancy, the table says.",
        )
        self.assertNotIn(ledger.RESTATEMENT_ECHOES_CLAIM, kinds(ledger_text(record)))


class ANumericClaimGetsANumericRestatement(unittest.TestCase):
    def test_a_number_answered_with_prose_is_a_finding(self):
        record = replace_field(
            CLEAN, "RESTATEMENT", "The source discusses leukocytosis in pregnancy."
        )
        self.assertIn(ledger.NUMERIC_CLAIM_UNQUANTIFIED, kinds(ledger_text(record)))

    def test_the_source_may_answer_in_its_own_units(self):
        """**Deliberately not a comparison.** The restatement is in the source's
        own terms by design, so a claim about 15,000 cells is rightly answered
        with a range in ``10^9/L`` and a digit-matching test would refuse the
        correct answer. This is the limit, pinned so it is not mistaken for one."""
        self.assertEqual(kinds(ledger_text(CLEAN)), [])

    def test_a_claim_with_no_number_is_not_asked_for_one(self):
        record = CLEAN.replace("A white count of 15,000 is", "Leukocytosis is", 1)
        record = replace_field(
            record, "RESTATEMENT", "The table reports a raised white cell count in normal pregnancy."
        )
        self.assertNotIn(ledger.NUMERIC_CLAIM_UNQUANTIFIED, kinds(ledger_text(record)))


class TheRecencyRuleIsTheAmendedOne(unittest.TestCase):
    """#215's correction, pinned against the claim it was corrected by.

    The first version cut a correct 2018 refutation for being old and would have
    left the 1932 teaching it refutes standing by default. What the rule refuses
    is a claim that is old **and superseded**, which is why an old source with a
    reason passes and an old source without one does not.
    """

    def _aged(self, year: int, recency: str) -> str:
        record = with_reference(CLEAN, f"Someone, A. ({year}). A study. Journal, 1(1), 1-9.")
        return ledger_text(replace_field(record, "RECENCY", recency))

    def test_an_old_source_with_no_excuse_is_a_finding(self):
        self.assertIn(ledger.STALE_UNEXCUSED, kinds(self._aged(2011, "current")))

    def test_nothing_newer_with_a_reason_stands(self):
        text = self._aged(2018, "nothing newer - the 1932 study it refutes has never been replicated.")
        self.assertEqual(kinds(text), [])

    def test_a_guideline_in_force_stands_on_its_own_date(self):
        """A current society document resting on a 2011 trial is a current source,
        and a 2013 KDIGO threshold is *the* threshold rather than an outdated one."""
        text = self._aged(2013, "guideline in force - KDIGO has issued no superseding lipid guideline.")
        self.assertEqual(kinds(text), [])

    def test_a_bare_excuse_is_the_assertion_without_the_looking(self):
        self.assertEqual(kinds(self._aged(2011, "nothing newer")), [ledger.BARE_EXCUSE])

    def test_the_window_boundary_is_five_years_inclusive(self):
        self.assertEqual(kinds(self._aged(AS_OF.year - 5, "within five")), [])
        self.assertIn(ledger.STALE_UNEXCUSED, kinds(self._aged(AS_OF.year - 6, "within five")))

    def test_the_window_is_measured_against_the_ledger_date_not_the_clock(self):
        """A ledger graded twice, a year apart, has to grade the same both times.

        **The read date moves back with the earlier grading date**, because #231's
        row is measured against ``DATE`` too: a ledger regraded as of 2024 cannot
        also say its source was read in 2026. That is the fixture being made
        coherent, not the row being worked around.
        """
        text = self._aged(2019, "current").replace("read 2026-08-19", "read 2023-11-02")
        self.assertEqual(kinds(text, date(2024, 1, 1)), [])
        self.assertIn(ledger.STALE_UNEXCUSED, kinds(text, date(2026, 1, 1)))

    def test_an_ab_disambiguated_year_still_parses(self):
        """``2019a`` is the form ``reference/apa7.md`` section 3 requires."""
        record = with_reference(
            CLEAN, "Someone, A. (2024a). A thing. Journal, 1(1), 1-9."
        )
        self.assertEqual(ledger.read_records(ledger_text(record))[0].reference_year, 2024)


class ARecencyDispositionComesFromTheVocabulary(unittest.TestCase):
    """``STATUS``'s reasoning arriving at the field beside it, which is where the
    first version of this module did not put it.

    ``RECENCY`` gates the window row, so a fifth disposition is a record the
    window never read -- the same argument that makes an unrecognized ``STATUS``
    a failure rather than a counted curiosity. Found by review.
    """

    def test_every_declared_disposition_passes(self):
        """Each against a reference the disposition is honest about, so a failure
        here is the vocabulary and never the window."""
        recent = "Someone, A. (2025). A study. Journal, 1(1), 1-9."
        for name in ledger.RECENCY_VALUES:
            excuse = name in ledger.EXCUSES
            value = f"{name} - searched, nothing later." if excuse else name
            record = replace_field(CLEAN, "RECENCY", value)
            if not excuse:
                record = with_reference(record, recent)
            with self.subTest(recency=name):
                self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_fifth_disposition_is_a_finding(self):
        record = replace_field(CLEAN, "RECENCY", "probably fine, did not look")
        self.assertIn(ledger.UNKNOWN_RECENCY, kinds(ledger_text(record)))

    def test_a_fifth_disposition_on_an_old_source_also_reports_the_window(self):
        """The two rows are different failures and both are true of that record."""
        record = with_reference(CLEAN, "Someone, A. (2011). A study. Journal, 1(1), 1-9.")
        record = replace_field(record, "RECENCY", "probably fine")
        found = kinds(ledger_text(record))
        self.assertIn(ledger.UNKNOWN_RECENCY, found)
        self.assertIn(ledger.STALE_UNEXCUSED, found)

    def test_case_is_free_and_punctuation_is_not(self):
        """``SOURCE`` is matched through ``normalize`` and this is not, because
        here the keyword is a prefix with a reason after it and normalizing
        destroys the boundary. So a hyphenated variant is a visible wrong word --
        which is the whole posture of a fixed vocabulary."""
        loud = replace_field(CLEAN, "RECENCY", "Nothing Newer - searched, nothing later.")
        self.assertEqual(kinds(ledger_text(loud)), [])
        hyphenated = replace_field(CLEAN, "RECENCY", "nothing-newer - searched, nothing later.")
        found = kinds(ledger_text(hyphenated))
        self.assertIn(ledger.UNKNOWN_RECENCY, found)
        self.assertIn(ledger.STALE_UNEXCUSED, found)

    def test_a_missing_recency_reports_the_missing_field_and_not_a_fifth_word(self):
        found = kinds(ledger_text(replace_field(CLEAN, "RECENCY", None)))
        self.assertIn(ledger.MISSING_FIELD, found)
        self.assertNotIn(ledger.UNKNOWN_RECENCY, found)


class APrefixIsNotAWord(unittest.TestCase):
    """#253. ``keyword_of`` matched on ``startswith`` alone, so any value whose
    first token merely *begins with* a vocabulary word was read as that word, and
    the rest of that token was absorbed into the remainder -- which is the field
    the substance rows then read as a reason.

    **The cases that graded *clean* are the ones to notice, and they are not the
    one #253's title names.** ``STATUS: unsourced-but-see-below`` reported **no
    findings at all**, its substance row satisfied by ``-but-see-below`` -- the
    residue of the keyword it was keyed on. ``RECENCY: nothing newerish`` did the
    same one field over, where the excuse is what the **window** reads, so an old
    reference passed with no excuse, no reason and nothing reported.

    **``RECENCY: currently under review`` is weaker than every copy of this claim
    said, and the correction is worth more than the case.** ``current`` is not in
    ``EXCUSES``, so the window fired on it before the fix as well; only
    ``UNKNOWN_RECENCY`` was lost. The consequence was copied out of #253's table
    while only its keyword column was re-derived, which is the failure this class
    caught in that table's *second* row -- committed in the fix for it, and caught
    afterwards by the tracker sweep. Both directions are pinned below so neither
    the strong case nor the weak one can be restated wrongly again.

    **No test in this file distinguished ``current`` from ``currently`` before
    these**, which is why the ticket asked for them ahead of the fix: a green run
    over the old cases proves less than it looks like it does.

    **The hyphen is the one character that needed a ruling rather than a copy.**
    ``RECENCY: nothing newer - searched 2026-08-19`` is the documented form, so a
    **spaced** hyphen has to be a separator; a **welded** one is part of the word,
    and no legitimate value of the vocabularies this module hands ``keyword_of``
    opens with a welded hyphenated form -- checked against the tree rather than
    assumed. **Which vocabularies those are is read off the module** rather than
    listed here, so a fourth cannot arrive with the loops below still green. ``SOURCE`` is out of it entirely, matched by normalized equality
    against ``_CLASS_KEYS``, which is also where the only hyphen inside a
    vocabulary word lives: ``peer-reviewed``.
    """

    VOCABULARIES = vocabularies_keyword_of_serves()

    def test_the_instrument_is_live(self):
        """The two loops below are only worth anything if the walk found the
        calls: rename ``keyword_of`` and they would pass over an empty set and
        report as coverage. ``test_build_artifacts_ignored``'s own first version
        passed three of four assertions against a check that said yes to
        everything, and this is the same guard one file over."""
        self.assertTrue(self.VOCABULARIES)
        self.assertTrue(all(self.VOCABULARIES.values()))

    def test_the_helper_keeps_the_whole_value_when_the_first_token_is_longer(self):
        """The remainder is what the substance rows read, so absorbing ``ly under
        review`` into it is what let the record pass wearing a reason."""
        self.assertEqual(
            ledger.keyword_of("currently under review", ledger.RECENCY_VALUES),
            ("", "currently under review"),
        )

    def test_the_helper_still_splits_the_documented_form(self):
        """The other direction, and the one a boundary rule is most likely to break:
        every documented record writes its reason after a spaced hyphen."""
        self.assertEqual(
            ledger.keyword_of("nothing newer - searched 2026-08-19", ledger.RECENCY_VALUES),
            ("nothing newer", " - searched 2026-08-19"),
        )

    def test_a_recency_under_review_is_not_a_recency_of_current(self):
        """``UNKNOWN_RECENCY`` is the whole of what this case discriminates.

        The ``STALE_UNEXCUSED`` beside it is asserted **because it fired before the
        fix too** -- ``current`` is not an excuse, so the window always read this
        record. Pinning it is what stops the weak case being restated as the strong
        one a third time; the strong one is two tests below.
        """
        record = replace_field(CLEAN, "RECENCY", "currently under review")
        found = kinds(ledger_text(record))
        self.assertIn(ledger.UNKNOWN_RECENCY, found)
        self.assertIn(ledger.STALE_UNEXCUSED, found)

    def test_a_welded_suffix_on_an_excuse_is_the_silent_pass(self):
        """**This is the case the ticket was really about**, and no copy of the
        claim named it until the sweep re-derived the table.

        ``nothing newer`` and ``guideline in force`` are the two words that excuse
        an old source, so a value merely opening with one took the window down with
        it. Before the fix ``RECENCY: nothing newerish`` on the 2009 reference in
        ``CLEAN`` reported **nothing at all** -- no fifth disposition, no window, no
        bare excuse, because ``ish`` is substance. A silent clean pass on a record
        that never said why the source stands.
        """
        for value in ("nothing newerish", "guideline in forceful terms"):
            with self.subTest(recency=value):
                found = kinds(ledger_text(replace_field(CLEAN, "RECENCY", value)))
                self.assertIn(ledger.UNKNOWN_RECENCY, found)
                self.assertIn(ledger.STALE_UNEXCUSED, found)

    def test_the_tickets_second_recency_row_is_wrong_and_is_kept_as_one(self):
        """#253's table lists ``RECENCY: currency of this guideline is unclear`` as
        grading ``current``. **It does not and never did** -- ``currency`` parts
        from ``current`` at the seventh character, so this value was already a
        fifth disposition before the fix and this case discriminates nothing. Kept
        rather than deleted, because a case passing for a different reason than the
        table beside it gives is exactly what a green run hides; re-derived here
        rather than taken from the ticket, which is what found it."""
        record = replace_field(CLEAN, "RECENCY", "currency of this guideline is unclear")
        self.assertIn(ledger.UNKNOWN_RECENCY, kinds(ledger_text(record)))
        self.assertEqual(ledger.keyword_of("currency", ledger.RECENCY_VALUES)[0], "")

    def test_a_status_that_merely_begins_with_one_is_a_third_word(self):
        """``sourcedish`` rather than the ticket's ``unsourced-but-see-below``,
        because the two fail for different reasons and only this one reaches the
        plain no-punctuation case; the welded hyphen has its own test below."""
        record = replace_field(CLEAN, "STATUS", "sourcedish")
        self.assertEqual(kinds(ledger_text(record)), [ledger.UNKNOWN_STATUS])

    def test_a_refutation_that_merely_begins_with_one_is_a_third_word(self):
        """``standstill on the publisher's side`` says nothing about the citation
        and used to pass the one verification row in the arrangement."""
        record = replace_field(CLEAN, "REFUTATION", "standstill on the publisher's side")
        found = kinds(ledger_text(record))
        self.assertIn(ledger.UNKNOWN_REFUTATION, found)
        self.assertNotIn(ledger.REFUTED_CITATION, found)

    def test_a_welded_hyphen_is_part_of_the_word(self):
        """The excluded character, on the branch selector -- and the other silent
        pass. Before the fix this record produced **no findings**: read as
        ``unsourced``, its substance row was satisfied by ``-but-see-below``, so a
        record saying nothing about what was searched cleared the row that exists
        to make it say so."""
        record = replace_field(CLEAN, "STATUS", "unsourced-but-see-below")
        self.assertEqual(kinds(ledger_text(record)), [ledger.UNKNOWN_STATUS])

    def test_no_vocabulary_word_survives_a_welded_continuation(self):
        """The ruling made runnable, across all three vocabularies at once."""
        for name, vocabulary in self.VOCABULARIES.items():
            for word in vocabulary:
                with self.subTest(vocabulary=name, word=word):
                    self.assertEqual(
                        ledger.keyword_of(f"{word}-free and clear", vocabulary),
                        ("", f"{word}-free and clear"),
                    )

    def test_a_spaced_hyphen_stays_a_separator(self):
        """The other direction, and the reason the exclusion had to be ruled on
        rather than copied: this is the form every documented record writes."""
        for name, vocabulary in self.VOCABULARIES.items():
            for word in vocabulary:
                with self.subTest(vocabulary=name, word=word):
                    self.assertEqual(
                        ledger.keyword_of(f"{word} - a reason", vocabulary),
                        (word, " - a reason"),
                    )

    def test_ordinary_punctuation_closes_the_keyword(self):
        """A reason is not always introduced by a hyphen, and refusing one that is
        not would be a new rule rather than this fix."""
        for separator in (",", ".", ":", ";", "—"):
            with self.subTest(separator=separator):
                record = replace_field(
                    CLEAN, "REFUTATION", f"stands{separator} the volume and pages match."
                )
                self.assertEqual(kinds(ledger_text(record)), [])


class TheDatelessLedgerLosesTheThreeRowsMeasuredAgainstTheDate(unittest.TestCase):
    """The five-year window, #231's read date, and #498's stated expiry.

    All three compare a date to ``DATE`` and none can run without one.
    """

    def test_an_old_source_is_not_reported_without_a_date_to_measure_against(self):
        record = with_reference(CLEAN, "Someone, A. (2011). A study. Journal, 1(1), 1-9.")
        record = replace_field(record, "RECENCY", "current")
        self.assertIn(ledger.STALE_UNEXCUSED, kinds(ledger_text(record)))
        self.assertEqual(kinds(ledger_text(record, stamp=""), None), [])

    def test_every_other_row_still_fires(self):
        for value, kind in (
            ("a blog post", ledger.UNKNOWN_SOURCE_CLASS),
            ("", ledger.MISSING_FIELD),
        ):
            with self.subTest(source=value):
                text = ledger_text(replace_field(CLEAN, "SOURCE", value), stamp="")
                self.assertIn(kind, kinds(text, None))


class AnUndatedReferenceIsRefusedUnlessAnExcuseStandsInForTheYear(unittest.TestCase):
    """``n.d.`` is legitimate APA, so refusing it outright would be a rule the
    clinician never made. The escape hatch is the one he did make."""

    UNDATED = "Nobody, N. (n.d.). Fundal height. Some Site."

    def test_n_d_with_nothing_said_about_it_is_a_finding(self):
        """The recency rule cannot be applied to it, and a row that could not be
        graded reads exactly like a row that passed."""
        record = with_reference(CLEAN, self.UNDATED)
        record = replace_field(record, "RECENCY", "current")
        self.assertIn(ledger.UNDATED_REFERENCE, kinds(ledger_text(record)))

    def test_n_d_with_an_excuse_and_a_reason_stands(self):
        record = with_reference(CLEAN, self.UNDATED)
        record = replace_field(
            record, "RECENCY", "nothing newer - the page states no revision date and CDC issues none."
        )
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_bare_excuse_does_not_buy_the_hatch(self):
        """Otherwise ``nothing newer`` alone would clear two rows at once."""
        record = with_reference(CLEAN, self.UNDATED)
        record = replace_field(record, "RECENCY", "nothing newer")
        found = kinds(ledger_text(record))
        self.assertIn(ledger.BARE_EXCUSE, found)
        self.assertIn(ledger.UNDATED_REFERENCE, found)

    def test_a_missing_reference_reports_the_missing_field_and_not_the_year(self):
        found = kinds(ledger_text(replace_field(CLEAN, "REFERENCE", None)))
        self.assertIn(ledger.MISSING_FIELD, found)
        self.assertNotIn(ledger.UNDATED_REFERENCE, found)


class TheAgentWritesDownWhatItRead(unittest.TestCase):
    """#231's first half. **No network in ``tools/``**: the agent that found the
    source was already on the page, so it records the locator and the date it
    read, and the grader compares them offline.

    **This narrows the hole rather than closing it.** An agent can write a URL it
    never opened. What the field buys is a specific a reader can be caught on in
    one click, where an APA entry alone is checkable only by going and looking --
    and a fabricated entry in correct APA form is the failure #214 calls the one
    that matters most, because it survives review.

    **Deliberately not exempt by source class.** ``tertiary reference`` is
    UpToDate, whose supplied topics the clinician hands over wholesale. A claim
    can reach this ledger through another research route, but that does not add
    its topic to the required companion-evidence set. Exempting the class would
    exempt the records that need the row most.
    """

    def test_a_url_is_a_locator(self):
        record = replace_field(CLEAN, "RESOLVED", "https://www.acog.org/clinical/x - read 2026-08-19")
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_bare_doi_is_a_locator(self):
        record = replace_field(CLEAN, "RESOLVED", "10.1097/AOG.0000000000002528 - read 2026-08-19")
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_prose_about_having_looked_is_not_a_locator(self):
        """The whole point is a specific the clinician can click."""
        record = replace_field(CLEAN, "RESOLVED", "found it on the society website - read 2026-08-19")
        self.assertIn(ledger.UNRESOLVABLE_LOCATOR, kinds(ledger_text(record)))

    def test_a_locator_with_no_read_date_is_a_finding(self):
        record = replace_field(CLEAN, "RESOLVED", "https://doi.org/10.1097/AOG.1")
        self.assertIn(ledger.UNDATED_READ, kinds(ledger_text(record)))

    def test_a_date_inside_the_url_is_not_the_read_date(self):
        """Anchored on the word, because a URL is full of digits and one of them
        being date-shaped is not the agent saying when it looked."""
        record = replace_field(CLEAN, "RESOLVED", "https://example.org/2026-08-19/topic")
        self.assertIn(ledger.UNDATED_READ, kinds(ledger_text(record)))

    def test_the_anchor_word_inside_the_url_is_not_the_read_date_either(self):
        """**The test above passed for the wrong reason** and this is the case it
        missed: an archive path spells the anchor word itself, so the locator
        supplied a read date the agent never wrote and graded itself as dated.
        Found by review, reproduced, then fixed."""
        record = replace_field(CLEAN, "RESOLVED", "https://site.org/read/2026-01-02/piece")
        self.assertIn(ledger.UNDATED_READ, kinds(ledger_text(record)))

    def test_a_slash_between_the_word_and_the_date_is_not_a_separator(self):
        self.assertIsNone(ledger.READ_DATE.search("read/2026-01-02"))
        self.assertIsNotNone(ledger.READ_DATE.search("- read 2026-01-02"))
        self.assertIsNotNone(ledger.READ_DATE.search("read: 2026-01-02"))

    def test_retrieved_is_accepted_beside_read(self):
        """``apa7.md`` section 4 calls it a retrieval date, so a run copying that
        word is writing the field correctly rather than wrongly."""
        record = replace_field(CLEAN, "RESOLVED", "https://doi.org/10.1/x - retrieved 2026-08-19")
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_source_read_after_the_paper_was_written_is_a_finding(self):
        record = replace_field(CLEAN, "RESOLVED", "https://doi.org/10.1/x - read 2026-09-02")
        self.assertIn(ledger.READ_AFTER_DATE, kinds(ledger_text(record)))

    def test_reading_it_the_day_the_paper_is_written_is_not(self):
        record = replace_field(CLEAN, "RESOLVED", "https://doi.org/10.1/x - read 2026-08-19")
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_read_date_is_not_graded_without_a_ledger_date_to_measure_against(self):
        record = replace_field(CLEAN, "RESOLVED", "https://doi.org/10.1/x - read 2026-09-02")
        self.assertEqual(kinds(ledger_text(record, stamp=""), None), [])

    def test_a_missing_resolved_reports_the_missing_field_and_not_a_bad_locator(self):
        record = replace_field(CLEAN, "RESOLVED", None)
        self.assertEqual(kinds(ledger_text(record)), [ledger.MISSING_FIELD])


class ThePageYearIsCheckedAgainstTheEntry(unittest.TestCase):
    """The year the page states, against the year the APA entry states. This is
    the row a fabricated citation has to get past, and it is why the field is two
    things rather than one: a year alone is an assertion, a year with where it was
    found is a place a reader can go and look."""

    def test_a_matching_year_passes(self):
        self.assertEqual(kinds(ledger_text(CLEAN)), [])

    def test_a_disagreeing_year_is_what_the_field_exists_for(self):
        record = replace_field(CLEAN, "PAGE-YEAR", "2011 - stated on the article masthead.")
        self.assertIn(ledger.PAGE_YEAR_DISAGREES, kinds(ledger_text(record)))

    def test_a_stated_page_year_against_an_n_d_entry_disagrees(self):
        """The page gave a year, so the entry should not read ``n.d.``"""
        record = replace_field(CLEAN, "REFERENCE", "Someone, A. (n.d.). A topic. UpToDate.")
        self.assertIn(ledger.PAGE_YEAR_DISAGREES, kinds(ledger_text(record)))

    def test_an_n_d_entry_beside_a_page_that_states_no_year_agrees(self):
        """The two say the same thing, and refusing it would refuse legitimate
        APA -- the mistake ``UNDATED_REFERENCE`` was corrected for once already."""
        record = with_reference(CLEAN, "Someone, A. (n.d.). A topic. UpToDate.")
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_page_year_stating_no_year_against_a_dated_entry_is_a_finding(self):
        record = replace_field(CLEAN, "PAGE-YEAR", "the cover page did not say")
        self.assertIn(ledger.PAGE_YEAR_UNSTATED, kinds(ledger_text(record)))

    def test_a_bare_year_is_the_assertion_without_the_looking(self):
        record = replace_field(CLEAN, "PAGE-YEAR", "2009")
        self.assertIn(ledger.BARE_PAGE_YEAR, kinds(ledger_text(record)))

    def test_a_bare_year_that_agrees_is_not_also_read_as_disagreeing(self):
        record = replace_field(CLEAN, "PAGE-YEAR", "2009")
        self.assertNotIn(ledger.PAGE_YEAR_DISAGREES, kinds(ledger_text(record)))

    def test_a_page_number_before_the_year_is_not_read_as_the_year(self):
        """**A four-digit page number is the shape that broke this**, and the
        field's own documented form invites it -- it asks for the year *and where
        the page says so*, and nothing requires the year first. ``on page 1327,
        dated 2009`` read as the year 1327 and failed a correct record. Found by
        review, reproduced, then narrowed to plausible years."""
        record = replace_field(CLEAN, "PAGE-YEAR", "on page 1327, dated 2009")
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_page_number_that_is_itself_a_plausible_year_still_wins(self):
        """The limit that remains, pinned rather than claimed away: 1900-2099
        narrows the shape, it does not order the field."""
        record = replace_field(CLEAN, "PAGE-YEAR", "on page 2019, dated 2009")
        self.assertIn(ledger.PAGE_YEAR_DISAGREES, kinds(ledger_text(record)))

    def test_a_missing_page_year_reports_the_missing_field_and_not_a_disagreement(self):
        record = replace_field(CLEAN, "PAGE-YEAR", None)
        self.assertEqual(kinds(ledger_text(record)), [ledger.MISSING_FIELD])


class TheRefutationPassIsASecondAgentTryingToProveTheCitationWrong(unittest.TestCase):
    """#231's second half, and the only row in this module that is verification
    rather than a better-shaped promise.

    **An agent asked *is this right?* says yes.** So the brief is to refute, and
    the record carries what the attempt found. A ``refuted`` record is a
    **failure** and not an outcome -- unlike ``unsourced``, which the skill routes
    to ``PROPOSED`` honestly. A refuted citation is a false one sitting in the
    ledger, and the run rewrites the record or writes ``unsourced``; it does not
    draft from it.

    **What no row here reaches is that the refuter was a different agent.** *What
    a written instruction cannot do is fail* is #214's own sentence and it binds
    its own successor -- ``SKILL.md`` states the independence and the grader
    grades the record. One shape it does reach: a refutation that is the
    restatement pasted back is the first agent re-asserting rather than a second
    one checking, which is ``RESTATEMENT_ECHOES_CLAIM``'s trick one level up.
    """

    def test_a_disposition_with_a_reason_passes(self):
        self.assertEqual(kinds(ledger_text(CLEAN)), [])

    def test_a_refuted_citation_is_a_failure_and_not_an_outcome(self):
        record = replace_field(CLEAN, "REFUTATION", "refuted - 114(6) ends at page 1300.")
        self.assertIn(ledger.REFUTED_CITATION, kinds(ledger_text(record)))

    def test_a_third_disposition_is_a_finding(self):
        """``STATUS``'s reasoning and not ``SOURCE``'s: it gates the row below."""
        record = replace_field(CLEAN, "REFUTATION", "probably fine")
        self.assertIn(ledger.UNKNOWN_REFUTATION, kinds(ledger_text(record)))

    def test_a_third_disposition_does_not_also_report_the_row_it_skipped(self):
        record = replace_field(CLEAN, "REFUTATION", "probably fine")
        self.assertNotIn(ledger.REFUTED_CITATION, kinds(ledger_text(record)))

    def test_a_bare_disposition_is_the_assertion_without_the_checking(self):
        record = replace_field(CLEAN, "REFUTATION", "stands")
        self.assertIn(ledger.BARE_REFUTATION, kinds(ledger_text(record)))

    def test_a_bare_refutation_on_a_refuted_record_reports_both(self):
        record = replace_field(CLEAN, "REFUTATION", "refuted")
        found = kinds(ledger_text(record))
        self.assertIn(ledger.BARE_REFUTATION, found)
        self.assertIn(ledger.REFUTED_CITATION, found)

    def test_the_restatement_pasted_back_is_the_first_agent_reasserting(self):
        restatement = ledger.read_records(ledger_text(CLEAN))[0].value("RESTATEMENT")
        record = replace_field(CLEAN, "REFUTATION", "stands - " + restatement)
        self.assertIn(ledger.REFUTATION_ECHOES_RESTATEMENT, kinds(ledger_text(record)))

    def test_a_real_second_reading_passes(self):
        record = replace_field(
            CLEAN, "REFUTATION", "stands - the volume and pages match the publisher landing page."
        )
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_case_is_free(self):
        record = replace_field(CLEAN, "REFUTATION", "Stands - checked the publisher landing page.")
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_paywall_passes_because_the_wall_is_not_an_absence(self):
        """The clinician's ruling of 2026-08-19 on #231's decision 4. A live page
        whose title matches is evidence the document exists, which is most of what
        a fabricated citation cannot do."""
        record = replace_field(
            CLEAN,
            "REFUTATION",
            "paywalled - the topic page loads and the title and authors match; the body"
            " is behind the subscription.",
        )
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_bare_paywall_is_still_the_assertion_without_the_checking(self):
        """It passes, so what did match is the whole of its evidence."""
        record = replace_field(CLEAN, "REFUTATION", "paywalled")
        self.assertIn(ledger.BARE_REFUTATION, kinds(ledger_text(record)))

    def test_a_paywall_is_not_a_refusal(self):
        """The split is the ruling: *could not reach* is not *is not there*."""
        record = replace_field(CLEAN, "REFUTATION", "paywalled - the title and authors match.")
        self.assertNotIn(ledger.REFUTED_CITATION, kinds(ledger_text(record)))

    def test_a_paywalled_record_is_counted_so_a_clean_exit_cannot_hide_it(self):
        """**The mitigation for a weak disposition that passes.** A set all behind
        a wall has been checked far less than exit 0 suggests, and this line is the
        only place that shows."""
        record = replace_field(CLEAN, "REFUTATION", "paywalled - the title and authors match.")
        scan = ledger.survey(ledger.read_records(ledger_text(record)), AS_OF)
        self.assertEqual((scan.behind_a_paywall, scan.failing_records), (1, 0))
        self.assertIn("citations behind a paywall", ledger.format_report(scan, source="x.md"))

    def test_a_standing_record_is_not_counted_as_paywalled(self):
        scan = ledger.survey(ledger.read_records(ledger_text(CLEAN)), AS_OF)
        self.assertEqual(scan.behind_a_paywall, 0)

    def test_a_fourth_disposition_is_still_a_finding(self):
        record = replace_field(CLEAN, "REFUTATION", "probably fine")
        self.assertIn(ledger.UNKNOWN_REFUTATION, kinds(ledger_text(record)))

    def test_a_missing_refutation_reports_the_missing_field_and_not_a_third_word(self):
        record = replace_field(CLEAN, "REFUTATION", None)
        self.assertEqual(kinds(ledger_text(record)), [ledger.MISSING_FIELD])


class TheRefutationDeclaresASecondRoute(unittest.TestCase):
    """#500's two-half declared difference at the public record-finding seam."""

    def test_a_different_second_route_passes(self):
        self.assertEqual(kinds(ledger_text(CLEAN)), [])

    def test_the_field_is_parsed_and_required(self):
        record = ledger.read_records(ledger_text(CLEAN))[0]
        self.assertEqual(
            record.value("SECOND-ROUTE"),
            "publisher HTML -> journal PDF rendered at 600 dpi",
        )
        self.assertIn("SECOND-ROUTE", ledger.REQUIRED_WHEN_SOURCED)
        self.assertIn("SECOND-ROUTE", ledger.CITATION_FIELDS)

    def test_an_unsplit_route_is_a_finding(self):
        record = replace_field(CLEAN, "SECOND-ROUTE", "journal PDF at 600 dpi")
        self.assertEqual(kinds(ledger_text(record)), [ledger.UNSPLIT_SECOND_ROUTE])

    def test_either_bare_half_is_a_finding(self):
        for value in (" -> journal PDF at 600 dpi", "publisher HTML -> "):
            with self.subTest(value=value):
                record = replace_field(CLEAN, "SECOND-ROUTE", value)
                self.assertEqual(kinds(ledger_text(record)), [ledger.BARE_SECOND_ROUTE])

    def test_normalized_equal_halves_are_a_finding(self):
        record = replace_field(
            CLEAN,
            "SECOND-ROUTE",
            "journal PDF at 600 dpi -> Journal PDF, at 600 DPI",
        )
        self.assertEqual(kinds(ledger_text(record)), [ledger.SECOND_ROUTE_UNCHANGED])

    def test_the_three_kinds_are_attributed_to_500(self):
        for kind in (
            ledger.UNSPLIT_SECOND_ROUTE,
            ledger.BARE_SECOND_ROUTE,
            ledger.SECOND_ROUTE_UNCHANGED,
        ):
            with self.subTest(kind=kind):
                self.assertEqual(ledger.ROWS[kind], "#500")


class ASourceCanStateItsPublishedExpiry(unittest.TestCase):
    """#498's field at the record, report, and command seams."""

    def test_a_future_stated_expiry_passes(self):
        record = replace_field(
            CLEAN,
            "STATED-EXPIRY",
            "2034-08-01 - termination date on the rule's cover sheet",
        )
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_none_stated_passes(self):
        self.assertEqual(kinds(ledger_text(CLEAN)), [])

    def test_a_stated_expiry_at_or_before_the_ledger_date_fires(self):
        for expiry in ("2026-08-18", "2026-08-19"):
            with self.subTest(expiry=expiry):
                record = replace_field(
                    CLEAN,
                    "STATED-EXPIRY",
                    f"{expiry} - termination date on the rule's cover sheet",
                )
                self.assertEqual(
                    kinds(ledger_text(record)),
                    [ledger.STATED_EXPIRY_REACHED],
                )

    def test_a_deliberately_superseded_source_carries_a_reason_and_passes(self):
        record = replace_field(
            CLEAN,
            "STATED-EXPIRY",
            "2024-05-02, superseded cited deliberately - the claim traces policy history",
        )
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_an_unrecognized_disposition_is_a_finding(self):
        record = replace_field(CLEAN, "STATED-EXPIRY", "current")
        self.assertEqual(kinds(ledger_text(record)), [ledger.UNKNOWN_STATED_EXPIRY])

    def test_a_dateless_ledger_loses_the_expiry_comparison(self):
        record = replace_field(
            CLEAN,
            "STATED-EXPIRY",
            "2026-08-18 - termination date on the rule's cover sheet",
        )
        self.assertNotIn(
            ledger.STATED_EXPIRY_REACHED,
            kinds(ledger_text(record, stamp=""), None),
        )

    def test_the_report_prints_both_counts_on_every_run(self):
        dated = replace_field(
            CLEAN,
            "STATED-EXPIRY",
            "2034-08-01 - termination date on the rule's cover sheet",
        )
        superseded = replace_field(
            CLEAN,
            "STATED-EXPIRY",
            "2024-05-02, superseded cited deliberately - the claim traces policy history",
        )
        scan = ledger.survey(
            ledger.read_records(ledger_text(CLEAN, dated, superseded)),
            AS_OF,
        )
        report = ledger.format_report(scan, source="claims.md")
        self.assertIn("stated expiry                     2 of 3 sourced records name a date", report)
        self.assertIn("superseded cited deliberately     1", report)

    def run_main(self, *records: str) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "claims.md"
            path.write_text(ledger_text(*records), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = ledger.main([str(path)])
            return status, out.getvalue(), err.getvalue()

    def test_a_ledger_carrying_the_field_nowhere_exits_two(self):
        legacy = replace_field(CLEAN, "STATED-EXPIRY", None)
        status, _out, err = self.run_main(legacy)
        self.assertEqual(status, 2)
        self.assertIn("STATED-EXPIRY", err)

    def test_one_missing_field_in_a_migrated_ledger_is_a_finding(self):
        legacy = replace_field(CLEAN, "STATED-EXPIRY", None)
        status, out, err = self.run_main(CLEAN, legacy)
        self.assertEqual(status, 1)
        self.assertIn(ledger.MISSING_FIELD, out)
        self.assertNotIn("carries STATED-EXPIRY nowhere", err)

    def test_findings_outrank_the_not_scanned_banner(self):
        legacy = replace_field(CLEAN, "STATED-EXPIRY", None)
        failing = replace_field(legacy, "SOURCE", "a blog post")
        status, _out, err = self.run_main(failing)
        self.assertEqual(status, 1)
        self.assertIn("STATED-EXPIRY", err)

    def test_the_inventory_declares_the_transcription_limit(self):
        limits = {row.key: row for row in ledger.DECLARED_LIMITS}
        row = limits["stated-expiry-transcription-unverified"]
        self.assertIs(row.evidence, ledger.EvidenceDisposition.DECLARED_READING)


class TheQueuedFieldLimitsLandWithTheirFields(unittest.TestCase):
    def test_second_route_replaces_the_old_single_clause(self):
        limits = {row.key: row.limit for row in ledger.DECLARED_LIMITS}
        limit = limits["refutation-independence-unverified"]
        self.assertIn("different agent", limit)
        self.assertIn("actually took", limit)
        self.assertIn("opened anything", limit)

    def test_the_cadence_limit_carries_its_reader_owned_trigger(self):
        limits = {row.key: row for row in ledger.DECLARED_LIMITS}
        row = limits["publication-cadence-reader-owned"]
        self.assertIs(row.evidence, ledger.EvidenceDisposition.DECLARED_READING)
        self.assertIn("SECOND citation", row.limit)
        self.assertIn("SECOND distinct publisher", row.limit)
        self.assertIn("cannot fire mechanically", row.limit)


class AnUnsourcedRecordCarriesNoneOfTheCitationFields(unittest.TestCase):
    """``UNSOURCED_WITH_CITATION_FIELD``'s reasoning, widened by #231: a record saying
    it found no source may not carry a locator, a page year or a refutation
    either. The two statements contradict, and nothing else in the file can tell
    which was meant."""

    def _unsourced(self) -> str:
        record = replace_field(
            CLEAN, "STATUS", "unsourced - searched PubMed, IDSA and UpToDate, nothing addresses it."
        )
        for name in ledger.CITATION_FIELDS:
            record = replace_field(record, name, None)
        return record

    def test_an_unsourced_record_with_no_citation_fields_passes(self):
        self.assertEqual(kinds(ledger_text(self._unsourced())), [])

    def test_each_citation_field_contradicts_it_on_its_own(self):
        values = {
            "REFERENCE": "Someone, A. (2020). A study. Journal, 1(1), 1-9.",
            "RESOLVED": "https://doi.org/10.1/x - read 2026-08-19",
            "PAGE-YEAR": "2020 - on the masthead.",
            "REFUTATION": "stands - checked the landing page.",
            "SECOND-ROUTE": "publisher HTML -> journal PDF rendered at 600 dpi",
            "STATED-EXPIRY": "none stated",
        }
        self.assertEqual(set(values), set(ledger.CITATION_FIELDS))
        for name, value in values.items():
            with self.subTest(field=name):
                record = replace_field(self._unsourced(), "RECENCY", value)
                record = record.replace("RECENCY:", name + ":")
                self.assertEqual(kinds(ledger_text(record)), [ledger.UNSOURCED_WITH_CITATION_FIELD])

    def test_the_citation_fields_are_not_required_of_it(self):
        """An unsourced record has no citation, so asking it to refute one would
        refuse the honest outcome the ``PROPOSED`` block exists for."""
        self.assertEqual(kinds(ledger_text(self._unsourced())), [])


class TheReportCarriesNoClaimTextWithoutShow(unittest.TestCase):
    def setUp(self):
        record = replace_field(CLEAN, "SOURCE", "a blog post")
        self.scan = ledger.survey(ledger.read_records(ledger_text(record)), AS_OF)

    def test_the_default_report_prints_no_claim_and_no_field(self):
        report = ledger.format_report(self.scan, source="claims.md")
        self.assertNotIn("white count", report)
        self.assertNotIn("a blog post", report)

    def test_show_prints_them(self):
        report = ledger.format_report(self.scan, source="claims.md", show=True)
        self.assertIn("white count", report)
        self.assertIn("a blog post", report)

    def test_every_row_is_named_in_the_report_with_its_ticket(self):
        report = ledger.format_report(self.scan, source="claims.md")
        for kind in ledger.KINDS:
            with self.subTest(row=kind):
                self.assertIn(f"{ledger.ROWS[kind]} - {kind}", report)


class TheCommandExitsOnWhatItFound(unittest.TestCase):
    def _run(self, text: str, name: str = "claims.md") -> int:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / name
            path.write_text(text, encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                return ledger.main([str(path)])

    def test_a_clean_ledger_exits_zero(self):
        self.assertEqual(self._run(ledger_text(CLEAN)), 0)

    def test_a_failing_record_exits_one(self):
        self.assertEqual(self._run(ledger_text(replace_field(CLEAN, "SOURCE", "a blog post"))), 1)

    def test_no_arguments_exits_two(self):
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(ledger.main([]), 2)

    def test_a_missing_file_exits_two_rather_than_one(self):
        """Not having scanned is a different answer from having found nothing."""
        err = io.StringIO()
        with redirect_stderr(err):
            self.assertEqual(ledger.main(["no-such-ledger-here.md"]), 2)

    def test_a_ledger_with_no_records_exits_two(self):
        self.assertEqual(self._run("DATE: 2026-08-19\n\nprose about the run\n"), 2)

    def test_a_ledger_with_no_date_header_exits_two(self):
        """The limb that matters. Recency is graded against the day the paper is
        written, so a ledger with no date was never measured by #215's rule at
        all -- and every other row would print clean beside a rule that never ran."""
        self.assertEqual(self._run(ledger_text(CLEAN, stamp="")), 2)

    def test_a_finding_outranks_a_missing_date_header(self):
        """``differential_scan``'s ordering: returning 2 here would file the
        strongest thing known about the ledger under the weakest heading. The
        first version of this module returned 2, which is the one place it
        departed from both siblings without saying so."""
        self.assertEqual(
            self._run(ledger_text(replace_field(CLEAN, "SOURCE", "a blog post"), stamp="")), 1
        )

    def test_the_missing_date_banner_prints_beside_the_exit_one(self):
        """So the finding reads as a floor rather than as the whole."""
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "claims.md"
            path.write_text(
                ledger_text(replace_field(CLEAN, "SOURCE", "a blog post"), stamp=""),
                encoding="utf-8",
            )
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                ledger.main([str(path)])
        self.assertIn("no DATE:", err.getvalue())
        # Both rows measured against the date, not just the window. A banner
        # naming one of two understates the floor it exists to establish.
        self.assertIn("five-year window", err.getvalue())
        self.assertIn("read-date", err.getvalue())
        self.assertIn("NO DATE HEADER", out.getvalue())

    def test_a_dateless_ledger_still_grades_every_row_that_does_not_need_it(self):
        text = ledger_text(replace_field(CLEAN, "SOURCE", "a blog post"), stamp="")
        self.assertEqual(kinds(text, None), [ledger.UNKNOWN_SOURCE_CLASS])

    def test_the_exit_one_message_names_no_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "claims.md"
            path.write_text(ledger_text(replace_field(CLEAN, "SOURCE", "a blog post")), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                ledger.main([str(path)])
        self.assertNotIn("white count", out.getvalue() + err.getvalue())


class TheSkillSaysWhatThisChecks(ProseBind, unittest.TestCase):
    """``test_spelling_scan``'s rule: a scanner that has drifted from the file a
    reader opens is worse than none, because it reads as agreement."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")

    def test_the_skill_names_the_command(self):
        self.assertIn("python tools/research_ledger.py <claims-ledger>", self.skill)

    def test_the_skill_shows_every_field_the_parser_reads(self):
        """In the worked example rather than in prose, because the example is
        what a run copies."""
        example = self._worked_example()
        self.assertIn("DATE:", example)
        self.assertIn("CLAIM:", example)
        for name in ("STATUS", *ledger.REQUIRED_WHEN_SOURCED):
            with self.subTest(field=name):
                self.assertIn(f"{name}:", example)

    # One phrase per row. Keyed on the module's own tuple, so a row added without
    # a sentence in the skill fails here rather than quietly becoming a rule only
    # the scanner knows -- which is what ``AGENTS.md`` classes this tool by.
    ROW_PHRASES = {
        ledger.CITED_TOPIC_NOT_IN_EVIDENCE: (
            "an UpToDate topic cited here that the evidence dump does not carry"
        ),
        ledger.UNREADABLE_UPTODATE_ENTRY: (
            "an entry whose locator names an UpToDate topic and that states no"
            " database element"
        ),
        ledger.UNRESEARCHED_PRESCRIPTION: "a drug in an Rx table that no claim record names",
        ledger.DOSE_NOT_CLAIMED: "an order stating a dose whose claim record states no number",
        ledger.UNREADABLE_DRUG_ROW: "a prescription table with no readable drug row",
        ledger.MISSING_FIELD: "a field missing or empty",
        ledger.UNKNOWN_STATUS: "a `STATUS` that is neither word",
        ledger.BARE_STATUS: "an `unsourced` with nothing said about what was searched",
        ledger.UNSOURCED_WITH_CITATION_FIELD: "an `unsourced` record carrying a `REFERENCE`",
        ledger.UNKNOWN_SOURCE_CLASS: "a `SOURCE` outside the four",
        ledger.UNKNOWN_RECENCY: "a `RECENCY` outside the four",
        ledger.RESTATEMENT_ECHOES_CLAIM: "a `RESTATEMENT` that is the claim pasted back",
        ledger.NUMERIC_CLAIM_UNQUANTIFIED: "whose restatement carries none",
        ledger.UNDATED_REFERENCE: "a reference stating no year",
        ledger.STALE_UNEXCUSED: "more than five years before `DATE` with no excuse",
        ledger.BARE_EXCUSE: "an excuse with no reason after it",
        ledger.UNRESOLVABLE_LOCATOR: "a `RESOLVED` that is not a URL or a DOI",
        ledger.UNDATED_READ: "a `RESOLVED` that does not say when it was read",
        ledger.READ_AFTER_DATE: "read after the paper was written",
        ledger.PAGE_YEAR_UNSTATED: "a `PAGE-YEAR` stating no year",
        ledger.BARE_PAGE_YEAR: "a `PAGE-YEAR` that is a year and nothing else",
        ledger.PAGE_YEAR_DISAGREES: "a `PAGE-YEAR` that is not the year in `REFERENCE`",
        ledger.UNKNOWN_REFUTATION: "a `REFUTATION` outside the three",
        ledger.BARE_REFUTATION: "a `REFUTATION` with no reason after it",
        ledger.REFUTED_CITATION: "a `REFUTATION` reading `refuted`",
        ledger.REFUTATION_ECHOES_RESTATEMENT: "a `REFUTATION` that is the restatement pasted back",
        ledger.UNSPLIT_SECOND_ROUTE: "a `SECOND-ROUTE` with no ASCII `->` separator",
        ledger.BARE_SECOND_ROUTE: "a `SECOND-ROUTE` with an empty half",
        ledger.SECOND_ROUTE_UNCHANGED: "a `SECOND-ROUTE` whose normalized halves are equal",
        ledger.UNKNOWN_STATED_EXPIRY: "a `STATED-EXPIRY` outside the three forms",
        ledger.STATED_EXPIRY_REACHED: (
            "a stated expiry at or before `DATE` without the deliberate-supersession reason"
        ),
    }

    def test_the_skill_writes_out_every_row_the_grader_applies(self):
        """``AGENTS.md`` classes this tool as one a skill *names* rather than one
        it depends on, and that class is defined by the instruction being complete
        without the command. A row only the scanner knows breaks it."""
        for kind in ledger.KINDS:
            with self.subTest(row=kind):
                self.assertIn(kind, self.ROW_PHRASES, "row is not written into the skill")
                self.assertIn(self.ROW_PHRASES[kind], self.skill)

    def test_the_skill_declares_the_source_vocabulary(self):
        for name in ledger.SOURCE_CLASSES:
            with self.subTest(source=name):
                self.assertIn(f"`{name}`", self.skill)

    def test_the_skill_declares_the_recency_vocabulary(self):
        for name in ledger.RECENCY_VALUES:
            with self.subTest(recency=name):
                self.assertIn(f"`{name}`", self.skill)

    def test_the_skill_declares_both_statuses(self):
        for name in ledger.STATUSES:
            with self.subTest(status=name):
                self.assertIn(f"`{name}`", self.skill)

    def test_the_skill_declares_the_refutation_vocabulary(self):
        for name in ledger.REFUTATION_VALUES:
            with self.subTest(refutation=name):
                self.assertIn(f"`{name}`", self.skill)

    def test_the_skill_sends_a_different_agent_to_refute(self):
        """The independence is the whole of #231's second half and no row here
        can see it, so the instruction has to carry it."""
        self.assertIn("not the one that wrote the record", self.skill)
        self.assertIn("try to prove it wrong", self.skill)

    def test_the_skill_says_the_refutation_pass_needs_no_network_in_tools(self):
        """#231's decision 1: nothing in ``tools/`` touches the network, and the
        reason is that the agent is already on the page."""
        self.assertIn("No tool here touches the network", self.skill)

    def test_the_skill_carries_the_amended_recency_rule_and_not_the_retired_one(self):
        """#215's correction. The retired version cut a correct claim for being
        old, and a run reading it would cut one again."""
        self.assertIn("stands where nothing newer exists", self.skill)
        self.assertProseNotIn("five years the outside limit", self.skill)
        self.assertProseNotIn("written as historical or dropped", self.skill)

    def test_the_skill_keeps_one_writer_on_the_ledger(self):
        """#206. Two writers on one file lose records, and the grader has no
        expected count to notice a short ledger with."""
        self.assertIn("They return their record; they do not write it", self.skill)
        self.assertIn("Write the claim list down before spawning anything", self.skill)

    def test_the_skill_writes_down_the_fallback_for_a_harness_without_subagents(self):
        """#214's open question 1, and #218 takes the same answer."""
        self.assertIn("no subagent tool", self.skill)
        self.assertIn("one at a time in the main\ncontext", self.skill)

    def _flat(self) -> str:
        """The skill with its hard wraps collapsed.

        A phrase that fits on one line today is one line-length edit away from
        being invisible to every assertion keyed on it, which is the failure
        ``test_run_record_claim`` recorded against three of its own six items.
        """
        return " ".join(self.skill.split())

    def test_the_skill_points_at_the_declared_limit_inventory(self):
        self.assertIn("research_ledger.DECLARED_LIMITS", self._flat())
        self.assertNotIn("A clean scan is not a checked claim", self._flat())
        self.assertNotIn("A clean scan is not a sourced document", self._flat())

    def test_the_skill_scopes_the_evidence_row_to_uptodate(self):
        """The scope is companion-evidence membership, so a reader who loses it
        reads the row as firing on any source the dump lacks, which is
        ``skills/practicum-case-study/SKILL.md`` step 3's ordinary case."""
        self.assertIn("required supplied-source set", self._flat())
        self.assertIn("is left alone", self._flat())

    def test_the_skill_says_a_referred_to_topic_is_not_a_defect(self):
        """#298's *What must not come out of this*, which is the half of the
        ruling a later reader is likeliest to widen."""
        self.assertIn("is not a defect and is not graded", self._flat())

    def test_the_skill_sends_the_ledger_to_a_gitignored_directory(self):
        self.assertIn("<run-directory>/claims.md", self.skill)
        ledger_lines = [line for line in self.skill.splitlines() if "claims.md" in line]
        self.assertTrue(ledger_lines)
        self.assertFalse(any("output/" in line for line in ledger_lines))

    def test_the_worked_example_in_the_skill_passes_the_scanner(self):
        """**The one that catches drift a substring cannot see.** A documented
        record shape the grader would refuse teaches the next run to write a
        ledger that fails, and every string test above would still be green."""
        example = self._worked_example()
        records = ledger.read_records(example)
        self.assertEqual(len(records), 1, "the skill's example should hold one record")
        stamp = ledger.DATE_HEADER.search(example)
        self.assertIsNotNone(stamp, "the skill's example should carry a DATE header")
        as_of = date(int(stamp.group(1)), int(stamp.group(2)), int(stamp.group(3)))
        self.assertEqual([f.kind for f in ledger.record_findings(records[0], as_of)], [])

    def _worked_example(self) -> str:
        """The fenced block in ``practicum-case-study`` step 3 that shows a record.

        Walked line by line rather than matched with one regex: a non-greedy
        pattern over the whole file happily opens on the *closing* fence of the
        ``bash`` block above and returns the prose between two code blocks, which
        is what the first version of this did.
        """
        blocks: list[str] = []
        current: list[str] | None = None
        for line in self.skill.splitlines():
            if line.startswith("```"):
                if current is None:
                    current = []
                else:
                    blocks.append("\n".join(current) + "\n")
                    current = None
                continue
            if current is not None:
                current.append(line)
        self.assertIsNone(current, "an unclosed code fence in the skill")
        found = [b for b in blocks if ledger.CLAIM.search(b)]
        self.assertEqual(len(found), 1, "expected exactly one worked ledger example")
        return found[0]


class TheRowsSitInHelpersAndTheBranchingSitsInRecordFindings(unittest.TestCase):
    """#242's seam, pinned in code rather than described.

    **Both directions, and by AST rather than by what a fixture happens to fire.**
    That is ``test_reference_scan``'s ``BODY_ROWS`` instrument adopted for its
    reason: measuring a partition against the rows one record trips proves only
    that the record trips them, and a row that landed in the wrong helper without
    being written into that fixture leaves every assertion green.

    What it buys is that the seam cannot rot quietly. A #231 row appended inside
    ``_recency_findings`` fails here, and so does a #215 row appended inside
    ``_citation_findings`` -- which is the shape a later ticket would introduce by
    reaching for the value nearest to hand.
    """

    def _kinds_constructed_in(self, function: str) -> set[str]:
        """Rows built inside one helper, using the shared Finding walk."""
        return constructed_kinds(ledger, function)

    def _rows_for(self, ticket: str) -> set[str]:
        return {kind for kind, owner in ledger.ROWS.items() if owner == ticket}

    def test_the_citation_helper_holds_every_231_row_and_nothing_else(self):
        self.assertEqual(self._kinds_constructed_in("_citation_findings"), self._rows_for("#231"))

    def test_the_recency_helper_holds_every_215_row_and_nothing_else(self):
        self.assertEqual(self._kinds_constructed_in("_recency_findings"), self._rows_for("#215"))

    def test_the_second_route_helper_holds_every_500_row_and_nothing_else(self):
        self.assertEqual(
            self._kinds_constructed_in("_second_route_findings"),
            self._rows_for("#500"),
        )

    def test_the_stated_expiry_helper_holds_every_498_row_and_nothing_else(self):
        self.assertEqual(
            self._kinds_constructed_in("_stated_expiry_findings"),
            self._rows_for("#498"),
        )

    def test_the_draft_grader_holds_every_289_row_and_nothing_else(self):
        """#289's rows read the draft rather than a record, so they are the one
        group here that could not have gone into a record helper. Pinned in both
        directions for the class's own reason: a #214 row appended inside
        ``prescription_findings`` would be graded only where ``--draft`` was
        given, which is a row that runs sometimes and reads as one that runs."""
        self.assertEqual(
            self._kinds_constructed_in("prescription_findings"), self._rows_for("#289")
        )

    def test_the_rows_the_report_calls_not_graded_are_exactly_the_draft_rows(self):
        """``DRAFT_ROWS`` is what ``format_report`` prints *not graded* off, and
        ``ROWS`` is what a reader is sent to #289 by. Two lists of one set,
        which is the drift #220 was filed over -- so one asserts the other."""
        self.assertEqual(set(ledger.DRAFT_ROWS), self._rows_for("#289"))

    def test_the_branching_helper_holds_only_the_rows_the_branch_decides(self):
        """``record_findings`` keeps the two rows no helper can own: a claim with
        no text, and a status the branch below cannot read."""
        self.assertEqual(
            self._kinds_constructed_in("record_findings"),
            {ledger.MISSING_FIELD, ledger.UNKNOWN_STATUS},
        )

    OWNERS = (
        "record_findings",
        "_unsourced_findings",
        "_contract_findings",
        "_recency_findings",
        "_citation_findings",
        "_second_route_findings",
        "_stated_expiry_findings",
        # #289's, and the only one that is not handed a ``Record``. The count in
        # the name below is deliberately gone: it read *five* while the tuple
        # held six for the length of one edit, which is #143 at the shortest
        # range this file has caught it at.
        "prescription_findings",
        # #298's, and the second that is not handed a ``Record``: it grades the
        # ledger's citations against the evidence dump.
        "evidence_findings",
    )

    def test_the_citation_helper_grades_a_record_on_its_own(self):
        """The seam is a real one: called with nothing but the record and the
        date, it returns what ``record_findings`` returns for those rows."""
        record = replace_field(CLEAN, "RESOLVED", "on the society website - read 2026-08-19")
        record = replace_field(record, "REFUTATION", "probably fine")
        parsed = ledger.read_records(ledger_text(record))[0]
        alone = {f.kind for f in ledger._citation_findings(parsed, AS_OF)}
        whole = {f.kind for f in ledger.record_findings(parsed, AS_OF)}
        self.assertEqual(alone, {ledger.UNRESOLVABLE_LOCATOR, ledger.UNKNOWN_REFUTATION})
        self.assertEqual(alone, whole & self._rows_for("#231"))

    def test_the_echo_row_reads_the_restatement_off_the_record(self):
        """**The one value that used to cross the seam.** ``_citation_findings``
        re-reads ``RESTATEMENT`` rather than being handed it, so calling it alone
        catches the refutation pasting the restatement back."""
        restatement = ledger.read_records(ledger_text(CLEAN))[0].value("RESTATEMENT")
        record = replace_field(CLEAN, "REFUTATION", f"stands - {restatement}")
        parsed = ledger.read_records(ledger_text(record))[0]
        self.assertIn(
            ledger.REFUTATION_ECHOES_RESTATEMENT,
            [f.kind for f in ledger._citation_findings(parsed, AS_OF)],
        )


class ExactlyThreeRowsAreMeasuredAgainstTheDate(unittest.TestCase):
    """#242's stated payoff. The exit-2 banner claims a dateless ledger loses the
    window, the read date and the stated expiry and nothing else; before the split that claim was
    readable only by reading the whole grader, and nothing asserted it.

    **The behavioral half is the one that counts.** A signature can take ``as_of``
    and ignore it, so the test drives one ledger both ways and diffs.
    """

    def _both_ways(self, record: str) -> tuple[set[str], set[str]]:
        text = ledger_text(record)
        dated = set(kinds(text, AS_OF))
        undated = set(kinds(ledger_text(record, stamp=""), None))
        return dated, undated

    def test_the_three_date_rows_are_the_whole_of_what_a_date_buys(self):
        record = with_reference(CLEAN, "Someone, A. (2011). A study. Journal, 1(1), 1-9.")
        record = replace_field(record, "RECENCY", "current")
        record = replace_field(record, "RESOLVED", "https://doi.org/10.1/x - read 2027-01-01")
        record = replace_field(
            record,
            "STATED-EXPIRY",
            "2026-08-18 - termination date on the rule's cover sheet",
        )
        dated, undated = self._both_ways(record)
        self.assertEqual(
            dated - undated,
            {
                ledger.STALE_UNEXCUSED,
                ledger.READ_AFTER_DATE,
                ledger.STATED_EXPIRY_REACHED,
            },
        )
        self.assertEqual(undated - dated, set())

    def test_a_clean_record_is_clean_both_ways(self):
        dated, undated = self._both_ways(CLEAN)
        self.assertEqual(dated, set())
        self.assertEqual(undated, set())

    def test_only_three_helpers_take_the_date(self):
        """The signatures are where a reader sees it. #214's rows are measured
        against no date at all, which is why ``_contract_findings`` takes none."""
        takes = {
            name
            for name in TheRowsSitInHelpersAndTheBranchingSitsInRecordFindings.OWNERS
            if "as_of" in inspect.signature(getattr(ledger, name)).parameters
        } - {"record_findings"}
        self.assertEqual(
            takes,
            {"_recency_findings", "_citation_findings", "_stated_expiry_findings"},
        )


class TheFindingsComeBackInReportOrder(unittest.TestCase):
    """#242 sorted them by ``KINDS``, so where a helper is called is not something
    ``--show`` can see. The counts were already ordered that way and the finding
    list was not, which is two orderings of one tuple in one report."""

    # The module's own lookup rather than a second copy of it. A dict rebuilt here
    # would agree with ``KINDS`` while saying nothing about what the module sorts by,
    # which is the whole claim -- ``test_build_artifacts_ignored``'s finding.
    ORDER = ledger._KIND_ORDER

    def test_the_lookup_the_module_sorts_by_is_kinds(self):
        """The tests above take their order from ``_KIND_ORDER`` rather than
        rebuilding it, so one assertion has to hold it to ``KINDS`` -- otherwise a
        lookup and a report tuple that had drifted apart would agree with each
        other and every ordering test would be green about the wrong sequence."""
        self.assertEqual(
            self.ORDER, {kind: index for index, kind in enumerate(ledger.KINDS)}
        )

    def _other(self) -> str:
        """A second record, failing a row that sorts *before* the first record's.

        That is what makes the grouping visible: concatenated, the two records'
        runs interleave out of ``KINDS`` order, and sorted they would not.
        """
        record = replace_field(CLEAN, "CLAIM", None)
        record = record.replace(
            "## CLAIM: A white count of 15,000 is within physiologic leukocytosis in pregnancy.",
            "## CLAIM: A second claim, whose source class is not in the vocabulary.",
        )
        record = replace_field(record, "RESTATEMENT", "The source gives a range.")
        return replace_field(record, "SOURCE", "a blog post")

    def _many(self) -> str:
        """One record failing rows from all three rulings at once."""
        record = with_reference(CLEAN, "Someone, A. (2011). A study. Journal, 1(1), 1-9.")
        record = replace_field(record, "RECENCY", "current")
        record = replace_field(record, "SOURCE", "a blog post")
        record = replace_field(record, "RESOLVED", "on the society website")
        record = replace_field(record, "REFUTATION", "refuted - the DOI 404s.")
        return record

    def test_a_record_failing_several_rulings_comes_back_in_kinds_order(self):
        found = kinds(ledger_text(self._many()))
        self.assertGreater(len(found), 3, "the fixture should trip rows from all three rulings")
        self.assertEqual(found, sorted(found, key=lambda k: self.ORDER[k]))

    def test_a_row_appended_out_of_report_order_comes_back_in_it(self):
        """**The discriminator, and the fixture above is not one.** Most records
        trip their rows in an order that already agrees with ``KINDS``, so a test
        built from one would pass with the sort deleted -- which is what the first
        version of this class did. ``_recency_findings`` appends ``BARE_EXCUSE``
        before ``UNDATED_REFERENCE`` and ``KINDS`` lists them the other way, so a
        record tripping both is the one shape that tells the two apart."""
        record = replace_field(CLEAN, "RECENCY", "nothing newer")
        record = with_reference(record, "Someone, A. (n.d.). A study. Journal.")
        self.assertEqual(
            kinds(ledger_text(record)),
            [ledger.UNDATED_REFERENCE, ledger.BARE_EXCUSE],
        )

    def test_the_survey_orders_within_a_record_and_groups_by_record(self):
        """**The ordering is per record, and ``--show`` is grouped rather than
        sorted.** ``survey`` concatenates one sorted list per record, so a two-record
        ledger's findings are not globally in ``KINDS`` order and should not be --
        a reader wants one record's rows together. What the sort buys is that within
        a record, which helper appended a row is invisible.

        **The first version of this test asserted the global property** and passed
        because its fixture held one record: a claim wider than what it measured,
        which is the shape this repo keeps catching. The second record is here so
        the narrower claim is the one being made.
        """
        text = ledger_text(self._many(), self._other(), stamp="2026-08-19")
        records = ledger.read_records(text)
        self.assertEqual(len(records), 2, "the fixture should hold two records")
        scan = ledger.survey(records, AS_OF)

        for record in records:
            run = [f.kind for f in scan.findings if f.claim == record.claim]
            self.assertTrue(run, "each record in this fixture should fail something")
            self.assertEqual(run, sorted(run, key=lambda k: self.ORDER[k]))

        listed = [f.kind for f in scan.findings]
        self.assertNotEqual(
            listed,
            sorted(listed, key=lambda k: self.ORDER[k]),
            "this fixture should show that the whole list is grouped, not sorted",
        )

    def test_the_counts_and_the_findings_name_the_same_rows(self):
        """Two views of one tuple. The counts are in ``KINDS`` order because
        ``survey`` builds them by walking ``KINDS``; the findings name the same set."""
        scan = ledger.survey(ledger.read_records(ledger_text(self._many(), self._other())), AS_OF)
        self.assertEqual(
            [kind for kind, count in scan.counts if count],
            sorted({f.kind for f in scan.findings}, key=lambda k: self.ORDER[k]),
        )


class TheDoiBranchOfTheLocatorMatchesAPageRange(unittest.TestCase):
    """#242's second finding, documented rather than tightened.

    A DOI is a registrant prefix and a free-form suffix, so a page range wearing
    that shape matches. **Pinned as a known behavior rather than left to be
    rediscovered**, which is the whole of what the ticket asked for -- every other
    limit in this module is written down and this one was not.
    """

    def test_a_page_range_shaped_like_a_doi_matches(self):
        self.assertTrue(ledger.LOCATOR.search("pp. 10.1327/1400 vol"))
        self.assertTrue(ledger.LOCATOR.search("10.1097/AOG.0b013e3181c2bde8"))

    def test_prose_with_no_locator_shape_still_fails_the_row(self):
        """The row it serves is unweakened where it matters: *"on the society
        website"* is what the field was written to refuse, and still is."""
        record = replace_field(CLEAN, "RESOLVED", "on the society website - read 2026-08-19")
        self.assertIn(ledger.UNRESOLVABLE_LOCATOR, kinds(ledger_text(record)))

    def test_the_sibling_rows_still_ask_the_record_for_the_rest(self):
        """**Why it is affordable.** The locator row says *this is not a locator*,
        never *this locator is good*, and it is one of three. A ``RESOLVED`` full
        of page numbers passes this row and is still asked when the page was
        opened."""
        record = replace_field(CLEAN, "RESOLVED", "pp. 10.1327/1400")
        found = kinds(ledger_text(record))
        self.assertNotIn(ledger.UNRESOLVABLE_LOCATOR, found)
        self.assertIn(ledger.UNDATED_READ, found)

    LIMIT = "registrant prefix and a free-form suffix"
    TICKET = "clinical-skills/issues/242"

    def test_the_inventory_names_the_limit(self):
        limits = {row.key: row.limit for row in ledger.DECLARED_LIMITS}
        self.assertIn("doi-shape-overmatches", limits)

    def test_the_repo_level_prose_points_instead_of_copying(self):
        doc = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("research_ledger.DECLARED_LIMITS", doc)
        self.assertNotIn(self.LIMIT, doc)
        self.assertIn(self.TICKET, doc)


# --- #289: the draft's prescriptions against the ledger -----------------------


def rx_table(order: str, disp: str = "QS", sig: str = "Infuse one gram daily for infection.") -> str:
    """One prescription table in ``style.md`` section 8's six-row form.

    Written out in full rather than assembled from the drug row alone, because the
    parser keys on the ``Disp:``/``Sig:`` pair and a fixture omitting one would be
    testing a shape no run writes.

    **Three columns, and it was one until the merge that brought #293 in.** That
    ticket rebuilt this table -- row 1 carries three cells, the middle rows declare
    one and span, and the last declares two -- and every test in this file stayed
    green against the retired form, because a fixture is only ever the shape its
    author last looked at. ``TheDocumentedTableIsStillReadable`` below is what makes
    that a failure rather than a quiet drift, and it is why this docstring's own
    claim is not the guarantee.
    """
    return "\n".join(
        [
            "| | | |",
            "| --- | --- | --- |",
            "| `<patient>` | `DOB x-x-xxx` | `NPI # 0000000000` |",
            f"| `{order}` |",
            f"| `Disp: {disp}` |",
            f"| `Sig: {sig}` |",
            "| `<name> FNP-C, CEN, TCRN` |",
            "| `Refill: none` | `DEA number on file with pharmacy` |",
            "",
        ]
    )


def a_drug_claim(claim: str) -> str:
    """A clean record whose claim heading is ``claim``."""
    lines = CLEAN.splitlines()
    lines[0] = f"## CLAIM: {claim}"
    return "\n".join(lines) + "\n"


CEFTRIAXONE = "ceftriaxone 1 g IV q24h x 14 days"
CEFTRIAXONE_CLAIM = (
    "Ceftriaxone 1 g intravenously every 24 hours is the recommended parenteral"
    " regimen for pelvic inflammatory disease in pregnancy."
)
HEADLESS = "| |\n| --- |\n| `Disp: QS` |\n| `Sig: take one for pain.` |\n"


def rx_kinds(draft: str, *records: str) -> list[str]:
    """The prescription findings one draft and one ledger produce."""
    parsed = ledger.read_records(ledger_text(*records)) if records else []
    return [
        f.kind for f in ledger.prescription_findings(ledger.read_prescriptions(draft), parsed)
    ]


class ADrugRowIsReadOffTheDispSigPair(unittest.TestCase):
    """The parser's own seam, before any row grades anything.

    **Two anchors and never a row position.** ``differential_scan``'s first
    version read a refusal by position and failed in both directions at once, and
    the repair was a welded pair. A prescription table is the one place in a case
    study where ``Disp:`` and ``Sig:`` co-occur, and the drug row is the row above
    ``Disp:`` -- so the position is read relative to an anchor rather than counted
    from the top of a table whose header rows a run may or may not write.
    """

    def test_one_table_yields_one_drug_row(self):
        found = ledger.read_prescriptions(rx_table(CEFTRIAXONE))
        self.assertEqual([rx.drug for rx in found], ["ceftriaxone"])

    def test_the_drug_is_the_leading_token_and_the_rest_is_the_order(self):
        rx = ledger.read_prescriptions(rx_table(CEFTRIAXONE))[0]
        self.assertEqual(rx.drug, "ceftriaxone")
        self.assertEqual(rx.order, CEFTRIAXONE)
        self.assertTrue(rx.states_a_dose)

    def test_a_markdown_table_that_is_not_a_prescription_is_not_read(self):
        """A case study is full of tables -- the differential, the MDM, the
        faculty's questions. Only the pair makes one a prescription."""
        other = "| Differential | Discriminator |\n| --- | --- |\n| Appendicitis | RLQ pain |\n"
        self.assertEqual(ledger.read_prescriptions(other), [])

    def test_two_tables_yield_two_drug_rows(self):
        text = (
            rx_table(CEFTRIAXONE)
            + "\nSome prose between them.\n\n"
            + rx_table("metronidazole 500 mg PO q12h x 14 days")
        )
        self.assertEqual(
            [rx.drug for rx in ledger.read_prescriptions(text)],
            ["ceftriaxone", "metronidazole"],
        )

    def test_a_row_with_no_digit_states_no_dose(self):
        """``prenatal vitamin one tablet PO daily`` spells its number out, and the
        row asking for a quantified claim is not asked of it -- which is
        ``NUMERIC_CLAIM_UNQUANTIFIED``'s *a claim with no number is not asked for
        one*, one artifact over."""
        rx = ledger.read_prescriptions(rx_table("prenatal vitamin one tablet PO daily"))[0]
        self.assertFalse(rx.states_a_dose)

    def test_a_table_carrying_disp_and_no_sig_is_not_a_prescription(self):
        half = "| |\n| --- |\n| `ceftriaxone 1 g IV q24h` |\n| `Disp: QS` |\n"
        self.assertEqual(ledger.read_prescriptions(half), [])

    def test_a_prescription_table_with_nothing_above_disp_reads_no_drug(self):
        """The row exists so a table the parser cannot read is a finding rather
        than a table it silently drops -- the partial-coverage-reading-as-complete
        shape ``differential_scan`` was given its exit-2 limb for."""
        self.assertEqual([rx.drug for rx in ledger.read_prescriptions(HEADLESS)], [""])


class AContinuedHomeMedicationDeclaresItself(unittest.TestCase):
    """The clinician's ruling of 2026-08-19 on #289's decision 1: a record is
    required for every drug the run chose a number for, and a home medication
    continued unchanged at the patient's own dose is not one of them.

    **It fails closed, and that is the whole safety of the rule.** The grader
    never infers *new*; the exemption is a declaration the run has to write. A
    drug row that says nothing is graded, so the direction a lazy run drifts in is
    toward being asked for a record rather than away from it -- which is
    ``guidelines_catalog --draft``'s *a guessed answer here is worse than a blank
    one* arriving at a prescription.
    """

    CONTINUED = "Continued home medication: prenatal vitamin one tablet PO daily"

    def test_the_declaration_exempts_the_row(self):
        rx = ledger.read_prescriptions(rx_table(self.CONTINUED))[0]
        self.assertTrue(rx.exempt)
        self.assertEqual(rx.drug, "prenatal")

    def test_an_undeclared_row_is_graded(self):
        rx = ledger.read_prescriptions(rx_table("prenatal vitamin one tablet PO daily"))[0]
        self.assertFalse(rx.exempt)

    def test_a_delayed_order_is_stripped_and_still_graded(self):
        """``style.md`` section 8's other declaration. A delayed order is a dose
        the run chose that has not started yet, so it is the one declaration that
        strips without exempting."""
        rx = ledger.read_prescriptions(
            rx_table("Delayed order: metformin 500 mg PO BID, hold until the AKI resolves")
        )[0]
        self.assertEqual(rx.drug, "metformin")
        self.assertFalse(rx.exempt)
        self.assertTrue(rx.states_a_dose)

    def test_the_declaration_is_matched_whatever_its_case(self):
        rx = ledger.read_prescriptions(rx_table(self.CONTINUED.lower()))[0]
        self.assertTrue(rx.exempt)

    def test_a_word_merely_opening_with_the_declaration_is_not_one(self):
        """``keyword_of``'s #253 boundary arriving at the declarations. Without it
        a drug row is exempted by a prefix of the exemption, which is the silent
        pass that ticket was filed over."""
        rx = ledger.read_prescriptions(
            rx_table("Continued home medications reviewed: aspirin 81 mg PO daily")
        )[0]
        self.assertFalse(rx.exempt)


class EveryPrescribedDrugHasAClaimRecord(unittest.TestCase):
    """#289's expected set. ``research_ledger`` has no expected count of its own
    and says so, so a ledger holding six records where seven claims went out
    grades clean; the draft is where the seventh becomes visible.

    That is ``checks_ledger``'s arrangement -- an expected set the grader can
    report a *missing* member of -- with the set derived from the document the run
    wrote rather than from a table in this module.
    """

    def test_a_drug_with_a_record_naming_it_passes(self):
        self.assertEqual(rx_kinds(rx_table(CEFTRIAXONE), a_drug_claim(CEFTRIAXONE_CLAIM)), [])

    def test_a_drug_no_record_names_is_the_ticket_itself(self):
        """The Module 1 submission verbatim: a ledger whose records sourced the
        *disposition* -- pregnancy as an indication for admission and intravenous
        therapy -- beside a table ordering a specific dose."""
        found = rx_kinds(
            rx_table(CEFTRIAXONE),
            a_drug_claim(
                "Pregnancy is an indication for inpatient management of pelvic"
                " inflammatory disease with intravenous therapy."
            ),
        )
        self.assertEqual(found, [ledger.UNRESEARCHED_PRESCRIPTION])

    def test_an_exempt_row_is_never_asked_for_one(self):
        found = rx_kinds(
            rx_table("Continued home medication: prenatal vitamin one tablet PO daily"),
            a_drug_claim(CEFTRIAXONE_CLAIM),
        )
        self.assertEqual(found, [])

    def test_an_unreadable_drug_row_is_a_finding_and_not_a_silent_drop(self):
        self.assertEqual(rx_kinds(HEADLESS), [ledger.UNREADABLE_DRUG_ROW])

    def test_the_match_is_a_word_and_not_a_prefix(self):
        """``cefazolin`` must not be answered by a record about ``ceftriaxone``,
        and ``ceftriaxone`` must be answerable by a record naming it
        mid-sentence -- which is why the row is a word boundary."""
        found = rx_kinds(rx_table("cefazolin 2 g IV q8h"), a_drug_claim(CEFTRIAXONE_CLAIM))
        self.assertEqual(found, [ledger.UNRESEARCHED_PRESCRIPTION])

    def test_the_match_ignores_case(self):
        found = rx_kinds(rx_table("Ceftriaxone 1 g IV q24h"), a_drug_claim(CEFTRIAXONE_CLAIM))
        self.assertEqual(found, [])

    def test_seven_tables_and_three_declared_leaves_four_graded(self):
        """The ticket's own arithmetic, and the clinician's ruling read back off
        the parser: seven tables, three continued home medications, four records
        required."""
        draft = "".join(
            [
                rx_table(CEFTRIAXONE),
                rx_table("metronidazole 500 mg PO q12h"),
                rx_table("azithromycin 1 g PO once"),
                rx_table("Delayed order: metformin 500 mg PO BID, hold until the AKI resolves"),
            ]
            + [
                rx_table(f"Continued home medication: drug{n} one tablet PO daily")
                for n in range(3)
            ]
        )
        found = ledger.read_prescriptions(draft)
        self.assertEqual(len(found), 7)
        self.assertEqual(sum(1 for rx in found if rx.exempt), 3)
        self.assertEqual(len(rx_kinds(draft)), 4)


class AClaimForADosedDrugCarriesTheNumber(unittest.TestCase):
    """The chain the row exists for, and it is one link rather than a new check.

    A record naming the drug is not yet a record that sourced the *dose* -- and
    the one form of that a string test reaches is whether the claim was asked
    numerically at all. Where it was, ``NUMERIC_CLAIM_UNQUANTIFIED`` already
    forces the restatement to answer with a number. So the two rows compose into
    *the table's dose reaches a source*, which is as far as offline grading goes.
    """

    def test_a_dosed_row_answered_by_a_claim_with_no_number(self):
        found = rx_kinds(
            rx_table(CEFTRIAXONE),
            a_drug_claim("Ceftriaxone is first-line for pelvic inflammatory disease."),
        )
        self.assertEqual(found, [ledger.DOSE_NOT_CLAIMED])

    def test_a_dosed_row_answered_by_a_numeric_claim_passes(self):
        self.assertEqual(rx_kinds(rx_table(CEFTRIAXONE), a_drug_claim(CEFTRIAXONE_CLAIM)), [])

    def test_an_undosed_row_is_not_asked_for_a_number(self):
        found = rx_kinds(
            rx_table("prenatal vitamin one tablet PO daily"),
            a_drug_claim("A prenatal vitamin is continued unchanged through pregnancy."),
        )
        self.assertEqual(found, [])

    def test_any_one_naming_record_carrying_a_number_answers_the_row(self):
        """Two records may split the drug between them -- one on the indication,
        one on the dose -- and the row asks the set rather than the first match."""
        found = rx_kinds(
            rx_table(CEFTRIAXONE),
            a_drug_claim("Ceftriaxone is first-line for pelvic inflammatory disease."),
            a_drug_claim(CEFTRIAXONE_CLAIM),
        )
        self.assertEqual(found, [])

    def test_the_row_never_compares_the_numbers(self):
        """**The prohibition #289 closes with.** A dose depends on indication,
        weight, renal function, pregnancy and route, and a row refusing a correct
        dose for the wrong reason is #215's defect a fourth time. The reachable
        property is whether the dose was sourced, never whether it is right -- so
        a claim carrying a *different* number passes this row.
        """
        found = rx_kinds(
            rx_table(CEFTRIAXONE),
            a_drug_claim(
                "Ceftriaxone 250 mg intramuscularly once is the regimen for uncomplicated"
                " gonococcal infection."
            ),
        )
        self.assertEqual(found, [])


class TheDraftFlagIsGradedAndItsAbsenceIsDeclared(unittest.TestCase):
    """#289 at the command, where the coverage claim is made.

    **A zero beside a row that never ran is the whole defect this ticket is
    about**, one level up: the run cited a topic its own ledger recorded as
    unavailable, and three commands exited 0 over it. So the report never prints
    a zero for a row ``--draft`` did not switch on -- #258's ruling, arriving at
    the one grader in this directory that reads two files.
    """

    def _run(self, ledger_body: str, draft: str | None, *flags: str) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "claims.md"
            path.write_text(ledger_body, encoding="utf-8")
            argv = [str(path), *flags]
            if draft is not None:
                draft_path = Path(temp) / "draft.md"
                draft_path.write_text(draft, encoding="utf-8")
                argv += ["--draft", str(draft_path)]
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                status = ledger.main(argv)
            return status, out.getvalue(), err.getvalue()

    def test_without_the_flag_the_three_rows_read_not_graded(self):
        status, out, _ = self._run(ledger_text(CLEAN), None)
        self.assertEqual(status, 0)
        for kind in ledger.DRAFT_ROWS:
            with self.subTest(row=kind):
                line = next(l for l in out.splitlines() if kind in l)
                self.assertIn("not graded", line)

    def test_without_the_flag_the_coverage_line_says_why(self):
        """The one line a reader takes the clean exit's width from."""
        _, out, _ = self._run(ledger_text(CLEAN), None)
        self.assertIn("prescription drug rows", out)
        self.assertIn("no --draft was given", out)

    def test_with_the_flag_the_rows_carry_counts(self):
        """**Keyed on the row lines and not on the whole report**, because the
        coverage block below carries its own ``(not graded)`` qualifier and an
        earlier version of this asserted the string was absent from the page --
        which made a true claim about the rows by asserting a false one about the
        report."""
        _, out, _ = self._run(ledger_text(a_drug_claim(CEFTRIAXONE_CLAIM)), rx_table(CEFTRIAXONE))
        for kind in ledger.DRAFT_ROWS:
            with self.subTest(row=kind):
                self.assertNotIn("not graded", next(l for l in out.splitlines() if kind in l))
        self.assertIn("prescription drug rows           1", out)
        self.assertIn("continued unchanged, exempt    0", out)
        self.assertIn("needing a claim record         1", out)

    def test_a_half_anchored_table_is_counted_on_the_page(self):
        """#204's shape in a second tool: a draft whose Rx tables are mixed reads
        a subset, grades it, and prints the shrunken count. The exit-2 limb
        covers *no* table and never a short read, so the coverage line is what
        makes a partial read visible."""
        deviant = rx_table("metronidazole 500 mg PO q12h").replace("Disp: QS", "Dispense: QS")
        # A blank line between them, because two table blocks written flush are
        # one table in Markdown and one run to this parser -- which is correct,
        # and which made the first version of this test measure nothing.
        _, out, _ = self._run(
            ledger_text(a_drug_claim(CEFTRIAXONE_CLAIM)),
            rx_table(CEFTRIAXONE) + "\n" + deviant,
        )
        self.assertIn("prescription drug rows           1", out)
        self.assertIn("tables read with one anchor    1", out)

    def test_a_whole_table_is_not_counted_as_half_anchored(self):
        """The instrument, live. Without this the line above could read 1 for a
        clean draft and prove nothing."""
        _, out, _ = self._run(
            ledger_text(a_drug_claim(CEFTRIAXONE_CLAIM)), rx_table(CEFTRIAXONE)
        )
        self.assertIn("tables read with one anchor    0", out)

    def test_the_line_prints_on_every_graded_run(self):
        """#258's reasoning: a reader who has learned to read the qualifier takes
        its absence as the stronger claim."""
        _, clean, _ = self._run(ledger_text(a_drug_claim(CEFTRIAXONE_CLAIM)), rx_table(CEFTRIAXONE))
        self.assertIn("tables read with one anchor", clean)

    def test_a_short_read_is_outside_the_exit_status_and_says_so(self):
        """``block_scan``'s arrangement for a reading rather than a violation. A
        table carrying one anchor is *probably* a malformed prescription and this
        cannot know it is one, and #204's own question -- whether a short read may
        refuse -- is unruled."""
        deviant = rx_table("metronidazole 500 mg PO q12h").replace("Disp: QS", "Dispense: QS")
        status, out, _ = self._run(
            ledger_text(a_drug_claim(CEFTRIAXONE_CLAIM)),
            rx_table(CEFTRIAXONE) + "\n" + deviant,
        )
        self.assertEqual(status, 0)
        self.assertIn("(not graded)", out)

    def test_a_sourced_prescription_exits_zero(self):
        status, _, _ = self._run(
            ledger_text(a_drug_claim(CEFTRIAXONE_CLAIM)), rx_table(CEFTRIAXONE)
        )
        self.assertEqual(status, 0)

    def test_a_prescription_no_record_names_exits_one(self):
        """The ticket, end to end: a well-formed ledger, a clean reference list,
        and a dose nobody sourced."""
        status, _, err = self._run(
            ledger_text(a_drug_claim("Pregnancy is an indication for inpatient management.")),
            rx_table(CEFTRIAXONE),
        )
        self.assertEqual(status, 1)
        self.assertIn("reach no claim record", " ".join(err.split()))

    def test_the_failure_line_names_no_drug(self):
        """Counts only by default, on this module's own terms: a drug attached to
        an encounter is a patient's medication. The drug is in ``--show``, and
        ``--show`` output is PHI."""
        _, out, err = self._run(
            ledger_text(a_drug_claim("Pregnancy is an indication for inpatient management.")),
            rx_table(CEFTRIAXONE),
        )
        self.assertNotIn("ceftriaxone", out + err)

    def test_show_names_it(self):
        _, out, _ = self._run(
            ledger_text(a_drug_claim("Pregnancy is an indication for inpatient management.")),
            rx_table(CEFTRIAXONE),
            "--show",
        )
        self.assertIn("ceftriaxone", out)

    def test_a_draft_with_no_prescription_table_exits_two(self):
        """``differential_scan``'s reasoning. A draft whose prescriptions are
        written in a shape this parser does not read would otherwise report three
        zeros and read as a document whose every dose reaches a record."""
        status, _, err = self._run(ledger_text(CLEAN), "# A draft\n\nProse and no tables.\n")
        self.assertEqual(status, 2)
        self.assertIn("no prescription table found", err)

    def test_a_prescription_finding_outranks_a_missing_date_header(self):
        """``differential_scan``'s ordering, and the pair that can actually
        co-occur: an unreadable draft yields no findings at all, so the limb a
        prescription finding has to outrank is the dateless ledger. The banner
        prints beside it, so the exit 1 reads as a floor."""
        status, _, err = self._run(
            ledger_text(a_drug_claim("Pregnancy is an indication for inpatient management."), stamp=""),
            rx_table(CEFTRIAXONE),
        )
        self.assertEqual(status, 1)
        self.assertIn("carries no DATE:", err)

    def test_a_missing_draft_file_exits_two(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "claims.md"
            path.write_text(ledger_text(CLEAN), encoding="utf-8")
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                status = ledger.main([str(path), "--draft", str(Path(temp) / "gone.md")])
        self.assertEqual(status, 2)
        self.assertIn("no draft file named", err.getvalue())

    def test_the_flag_with_no_value_is_usage_and_not_a_silent_skip(self):
        """``--draft`` swallowing the next argument, or being dropped, are the two
        ways a run believes it graded its prescriptions and did not."""
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "claims.md"
            path.write_text(ledger_text(CLEAN), encoding="utf-8")
            err = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(err):
                status = ledger.main([str(path), "--draft"])
        self.assertEqual(status, 2)
        self.assertIn("usage:", err.getvalue())

    def test_the_ledger_path_is_not_eaten_by_the_flag(self):
        """The one-line ``[a for a in argv if not a.startswith("--")]`` filter this
        replaced would have read the draft's path as a second positional and, with
        the flag written first, the draft as the ledger."""
        parsed = run_grader.parse(
            ledger.GRADER, ["--draft", "d.md", "ledger.md", "--show"]
        )
        self.assertEqual((parsed.source, parsed.value("--draft"), parsed.show), ("ledger.md", "d.md", True))

    def test_the_equals_spelling_is_read_too(self):
        parsed = run_grader.parse(ledger.GRADER, ["ledger.md", "--draft=d.md"])
        self.assertEqual((parsed.source, parsed.value("--draft")), ("ledger.md", "d.md"))

    def test_a_following_flag_is_a_missing_value_and_not_a_path(self):
        """``--draft --show`` gave two wrong answers at once before the standards
        axis of `/code-review` priced it: it reported *no draft file named
        --show*, which is a claim about a path nobody wrote, and it swallowed
        ``--show`` so the findings could not be read either."""
        with self.assertRaises(run_grader.ParseError):
            run_grader.parse(ledger.GRADER, ["ledger.md", "--draft", "--show"])

    def test_an_absent_flag_is_none_and_not_an_empty_string(self):
        """Two different mistakes, and only one of them is a run that graded no
        prescriptions on purpose."""
        self.assertIsNone(run_grader.parse(ledger.GRADER, ["ledger.md"]).value("--draft"))
        with self.assertRaises(run_grader.ParseError):
            run_grader.parse(ledger.GRADER, ["ledger.md", "--draft"])


class ASubmissionDraftJoinsTheLedgerRun(unittest.TestCase):
    def test_a_different_run_key_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            run = root / "scratch" / "runs" / "nur5144-m1-case-study"
            run.mkdir(parents=True)
            claims = run / "claims.md"
            claims.write_text(ledger_text(CLEAN), encoding="utf-8")
            draft = root / "output" / "case-studies" / "nur5144-m2-case-study-2026-08-20.md"
            draft.parent.mkdir(parents=True)
            draft.write_text("# Draft\n", encoding="utf-8")
            stderr = io.StringIO()
            with (
                mock.patch.object(coursework_run, "output_root", return_value=root / "output"),
                mock.patch.object(coursework_run, "scratch_root", return_value=root / "scratch"),
                redirect_stdout(io.StringIO()),
                redirect_stderr(stderr),
            ):
                status = ledger.main([str(claims), "--draft", str(draft)])
        self.assertEqual(status, 2)
        self.assertIn("does not belong", stderr.getvalue())


class TheDocumentedTableIsStillReadable(unittest.TestCase):
    """Run the parser over `style.md` §8's own table, not over a fixture.

    **This class exists because the fixture went stale inside one merge.** #293
    rebuilt that table from one column to three while this branch was open, every
    test in this file stayed green against the retired form, and the only thing
    that caught it was reading the merged section by hand. That is
    [#86](https://github.com/mshamblin5150-code/clinical-skills/issues/86)'s *the
    merge is the unguarded moment* arriving on a **fixture** -- where no assertion
    can see it, because a fixture is only ever the shape its author last looked
    at.

    So the assertion is against the file a run copies, on
    ``TheSkillSaysWhatThisChecks``'s reasoning one artifact over: a documented
    table this parser cannot read teaches the next run to write prescriptions
    ``--draft`` reports as unreadable, and every substring test here would still
    be green.

    **What it asserts is structural and never the drug**, because the documented
    row is a template: ``<drug> <dose> <route> <frequency>`` is a placeholder and
    the parser rightly reads no drug out of it. What has to hold is that the
    ``Disp:``/``Sig:`` pair is found and that the row above ``Disp:`` is the one
    the drug would be in.
    """

    STYLE = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "style.md"

    @classmethod
    def setUpClass(cls):
        text = cls.STYLE.read_text(encoding="utf-8")
        opened = text.index("## 8. Rx")
        cls.section = text[opened : text.index("\n## ", opened + 1)]

    def test_the_documented_table_reads_as_one_prescription(self):
        found = ledger.read_prescriptions(self.section)
        self.assertEqual(len(found), 1, "style.md section 8's table is not read as a prescription")

    def test_the_row_above_disp_is_the_one_the_drug_goes_in(self):
        """The template's placeholder is not a drug, and the order it lands in is
        what says the parser found the right row rather than the patient row
        above it or the ``Disp:`` row itself."""
        found = ledger.read_prescriptions(self.section)[0]
        self.assertIn("<drug>", found.order)
        self.assertEqual(found.drug, "")

    def test_the_fixture_in_this_file_is_the_documented_shape(self):
        """**The narrow half, and the one that went stale.** Column counts, row
        order and the separator row are what the parser walks, so the fixture and
        the documented table have to agree about them -- and the cells' contents
        are the fixture's own business, since it fills in a real drug where the
        table writes a placeholder.
        """
        def skeleton(block: str) -> list[int]:
            return [
                len(_cells_of(line))
                for line in block.splitlines()
                if line.lstrip().startswith("|")
            ]

        def _cells_of(line: str) -> list[str]:
            return ledger._cells(line)

        documented = [
            line for line in self.section.splitlines() if line.lstrip().startswith("|")
        ]
        self.assertEqual(
            skeleton("\n".join(documented)),
            skeleton(rx_table("ceftriaxone 1 g IV q24h")),
            "style.md section 8's table and this file's fixture disagree about their shape",
        )


class TheStyleSheetDeclaresWhatTheParserReads(unittest.TestCase):
    """`style.md` §8 is the file a run copies; this module holds the vocabulary.

    **A scanner holding a different answer than the file a reader opens is worse
    than none, because it reads as agreement** -- ``test_spelling_scan``'s
    reasoning, and the arrangement ``checks_ledger`` uses with
    ``skills/practicum-case-study/SKILL.md`` step 9's table.
    Both files said *`tools/research_ledger.py --draft` reads both labels off this
    table* and nothing made that true; the standards axis of `/code-review` found
    it.

    **Derived in the test rather than at run time**, because a case study run is
    not a checkout and nothing this module does at run time can open `style.md`.

    **Matched against a whitespace-normalized copy**, because `style.md` hard-wraps
    and the first version of this class looked for `Continued home medication:`
    where the sheet writes `Continued home` and `medication:` on two lines. That
    is ``test_run_record_claim``'s finding exactly -- a search cannot see a phrase
    broken across a line, and it answers like a settled negative rather than
    saying it could not look.
    """

    STYLE = REPO_ROOT / "skills" / "practicum-case-study" / "reference" / "style.md"

    @classmethod
    def setUpClass(cls):
        text = cls.STYLE.read_text(encoding="utf-8")
        opened = text.index("## 8. Rx")
        cls.raw = text[opened : text.index(chr(10) + "## ", opened + 1)]
        cls.section = " ".join(cls.raw.split())

    def test_the_sheet_writes_every_declaration_the_parser_reads(self):
        for name in ledger.DRUG_ROW_DECLARATIONS:
            with self.subTest(declaration=name):
                self.assertIn(f"{name}:".capitalize(), self.section)

    def test_the_sheet_says_which_one_exempts(self):
        """The asymmetry is the ruling, so the sheet has to carry it: a delayed
        order is still a dose the run chose."""
        exempts, grades = ledger.EXEMPT_DECLARATIONS[0], ledger.DELAYED_ORDER
        self.assertIn(f"{exempts}:".capitalize(), self.section)
        self.assertIn(f"`{grades.capitalize()}:` exempts nothing", self.section)

    def test_the_wrapping_is_what_this_class_reads_through(self):
        """The instrument, live. Without it every assertion above is a search that
        could not have worked answering like a settled negative -- which is this
        repo's most-recorded shape, and it fired here on the first attempt."""
        self.assertNotIn(f"{ledger.CONTINUED_HOME}:".capitalize(), self.raw)
        self.assertIn(f"{ledger.CONTINUED_HOME}:".capitalize(), self.section)

    def test_the_worked_prose_block_cites_no_concrete_source(self):
        """#289's comment's live finding, pinned so a reword cannot undo it.

        That block modeled `(Workowski et al., 2021)` -- a CDC guideline the
        evidence dump cross-references and does not carry -- so the example taught
        citing a source the run had never read. It is a placeholder
        now, and **a prose edit putting a real citation back would have failed
        nothing**, which is #220's lesson and why this exists.
        """
        text = self.STYLE.read_text(encoding="utf-8")
        opened = text.index("### The prose block under each table")
        block = text[opened : text.index(chr(10) + "## ", opened + 1)]
        quoted = " ".join(
            line for line in block.splitlines() if line.startswith(">")
        )
        self.assertIn("<Author>", quoted, "the worked block lost its placeholder citation")
        self.assertEqual(
            re.findall(r"\((?!<)[A-Z][A-Za-z'-]+(?:[^)]*?),\s*(?:19|20)\d{2}[a-z]?\)", quoted),
            [],
            "the worked prose block models a concrete in-text citation again",
        )


class TheDoseRowAsksForANumberAndNotForTheNumber(unittest.TestCase):
    """``UNRESOLVABLE_LOCATOR``'s arrangement, one row over: a limit that is
    documented and pinned rather than tightened.

    The claim heading is written in the source's own terms **by design** -- this
    module's own ``NUMERIC_CLAIM_UNQUANTIFIED`` exists because a claim about
    15,000 cells is rightly answered in ``10^9/L`` -- so a digit test is the widest
    thing available and a heading carrying a year satisfies it. **It only ever
    weakens the weaker half of a pair**: the row says *this claim was not asked
    numerically*, never *this dose is sourced*, and ``UNRESEARCHED_PRESCRIPTION``
    still asks that a record exist at all.
    """

    def test_a_year_in_the_heading_satisfies_the_row(self):
        found = rx_kinds(
            rx_table(CEFTRIAXONE),
            a_drug_claim("Ceftriaxone is first-line for pelvic inflammatory disease since 2021."),
        )
        self.assertEqual(found, [], "the row is narrower than it is documented to be")

    def test_the_inventory_names_the_limit(self):
        limits = {row.key: row.limit for row in ledger.DECLARED_LIMITS}
        self.assertIn("dose-claim-accepts-any-number", limits)

    def test_the_sibling_row_still_asks_for_the_record(self):
        """Why it is affordable. A heading with a year and no drug fails the row
        above this one."""
        found = rx_kinds(rx_table(CEFTRIAXONE), a_drug_claim("Published in 2021."))
        self.assertEqual(found, [ledger.UNRESEARCHED_PRESCRIPTION])


class OneDrugRowIsOneDrugAndNothingHereMakesThatTrue(unittest.TestCase):
    """`#300`, documented rather than tightened, on ``UNRESOLVABLE_LOCATOR``'s
    terms: a limit a reader cannot find reads as coverage.

    **Found by the tracker sweep against `#127`**, whose shape is a count whose
    denominator the graded run chooses. `style.md` §8 says *one table per drug*
    and nothing grades it, so a run that welds two orders into one drug row makes
    the expected set come out right by formatting -- and the second drug's dose,
    which is exactly the recalled number `#289` was filed over, is invisible to
    all three rows.

    **Not narrowable here.** Splitting on ``and`` cuts ``normal saline and
    potassium chloride``, and telling two drugs apart needs a drug vocabulary,
    which is the table `#289` forbids in as many words.
    """

    BUNDLED = "doxycycline 100 mg PO BID x 7 days and metronidazole 500 mg PO TID x 7 days"

    def test_a_welded_row_is_one_drug(self):
        found = ledger.read_prescriptions(rx_table(self.BUNDLED))
        self.assertEqual([rx.drug for rx in found], ["doxycycline"])

    def test_the_second_drugs_dose_is_graded_by_nothing(self):
        """The finding, stated as a passing assertion so it cannot be mistaken
        for an oversight. Metronidazole is unsourced and the set is clean."""
        found = rx_kinds(
            rx_table(self.BUNDLED),
            a_drug_claim(
                "Doxycycline 100 mg twice daily for 7 days is the oral regimen for"
                " pelvic inflammatory disease."
            ),
        )
        self.assertEqual(found, [])

    def test_the_inventory_names_the_limit(self):
        limits = {row.key: row.limit for row in ledger.DECLARED_LIMITS}
        self.assertIn("welded-drug-hidden", limits)


class TheRowSplitIsTheRenderersOwn(unittest.TestCase):
    """``reference_scan``'s ``REFERENCE_HEADING`` precedent, and it is the same
    argument: ``docx_write.split_row`` decides where a cell ends in the document a
    grader reads, so a second reading of one table can put the ``Disp:`` anchor in
    a different row than the one that renders.

    Restated rather than imported until the standards axis of `/code-review`
    priced it, and the divergence was live: an escaped pipe splits a cell here
    and does not there, which is the defect #215's follow-up recorded costing a
    rendered cell.
    """

    def test_the_cells_come_from_the_renderer(self):
        self.assertIs(ledger.split_row, docx_write.split_row)

    def test_an_escaped_pipe_stays_one_cell(self):
        """The behavioral half. A signature is not enough: ``_cells`` could re-split
        what ``split_row`` returned."""
        self.assertEqual(ledger._cells(r"| `ceftriaxone 1 g \| held` |"), ["ceftriaxone 1 g | held"])

    def test_a_drug_row_carrying_an_escaped_pipe_is_still_one_drug(self):
        found = ledger.read_prescriptions(rx_table(r"ceftriaxone 1 g IV q24h \| pharmacy to verify"))
        self.assertEqual([rx.drug for rx in found], ["ceftriaxone"])

class TheWeldedRowIsAReadingThatIsAskedFor(unittest.TestCase):
    """`#300`'s ruling of 2026-08-20: the row above stays declared, and the reading
    it names is written into a brief a run has to answer.

    ``test_reference_scan.TheReadingTheCommandCannotDoIsAGradedCheck``'s
    arrangement, and it is here for that class's reason. Option 3 of the ticket --
    send it to ``skills/practicum-case-study/SKILL.md`` step 9's reader -- is a
    prose claim in two files on its own;
    what makes it more than that is
    [#240](https://github.com/mshamblin5150-code/clinical-skills/issues/240)'s
    grader over ``skills/practicum-case-study/SKILL.md`` step 9's fan-out, which
    fails a run returning no verdict on the row. **So this asserts the chain end to
    end** -- ``style.md`` section 8 names the reading, the step names it in the
    row's reader column, and ``checks_ledger`` expects that row by name.

    **The row was already the right reader and was simply not told.** Its brief
    has always asked whether every drug in the Plan has a table, and a welded row
    is exactly a drug in the Plan without one -- so the edit is one clause rather
    than a new check, which is why option 3 was the cheapest of the three.

    **What it cannot reach is the same thing every reading here cannot**: this
    binds that the reader was asked, never that the reader looked. That row's
    ``clean`` is one ``checks_ledger`` does not require to say what it walked --
    [#255](https://github.com/mshamblin5150-code/clinical-skills/issues/255) ruled
    which rows do and this is not one -- so a bare ``clean`` from a reader that
    skimmed still passes, and that is the standing price of the option.
    """

    ROW = "the Rx blocks"
    READING = "welds a second drug"

    def test_the_grader_still_expects_the_row_by_name(self):
        self.assertIn(self.ROW, checks_ledger.EXPECTED_CHECKS)

    def row_line(self):
        """The ``skills/practicum-case-study/SKILL.md`` step 9 table row, as one physical line.

        A table row is one line in that file, so the row and its reader column are
        read together and no cell of the row below can satisfy the assertion.
        """
        for line in SKILL.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("|") and self.ROW in stripped:
                return stripped
        return None

    def test_the_step_names_the_row(self):
        self.assertIsNotNone(
            self.row_line(),
            "skills/practicum-case-study/SKILL.md step 9 no longer carries the row",
        )

    def test_the_rows_reader_column_names_the_welded_row(self):
        line = self.row_line()
        self.assertIsNotNone(
            line,
            "skills/practicum-case-study/SKILL.md step 9 no longer carries the row",
        )
        self.assertIn(self.READING, line)

    def test_the_by_eye_walk_names_it_too(self):
        """The same step's by-eye list, which is what a harness with no subagent
        tool walks instead. Naming the direction in the table row alone would put
        it out of reach of exactly the run that has no reader to send."""
        step = SKILL.read_text(encoding="utf-8")
        step = " ".join(step[step.index("### 9. Check") :].split())
        self.assertIn(self.READING, step[step.index("Then walk this list, by eye") :])

    def test_the_rule_is_written_where_the_rule_lives(self):
        """``style.md`` section 8 is where *one table per drug* is stated, so it is
        where the way that rule is broken belongs. A reading briefed in the step
        and absent from the sheet is a rule with no statement behind it.

        **Whitespace-normalized, like its sibling above and for the same reason**:
        every phrase in that sheet is hard-wrapped, and a phrase broken across two
        lines is invisible to a substring search -- ``test_run_record_claim``'s
        finding. This assertion read the file raw for one review, which is two
        instruments for one claim and is the weaker of them going unnoticed.
        """
        text = " ".join(STYLE.read_text(encoding="utf-8").split())
        section = text[text.index("## 8.") : text.index("## 9.")]
        self.assertIn(self.READING, section)
        self.assertIn("One table per drug", section)


class TheDeclinedParserRowsFireOnCorrectOrders(unittest.TestCase):
    """Why `#300` was ruled a reading rather than a row, re-derived rather than
    cited.

    **The ticket's decision 2 is the option a later session will re-propose**,
    because it looks obvious: *a drug row whose text after the first dose contains
    a second unit-bearing token*. It is refused on a measurement, and the
    measurement is here so that re-proposing it costs a failing test rather than
    an argument -- ``threshold_sheet.py``'s two heuristics tried against the corpus
    before the constant was chosen, and
    [#278](https://github.com/mshamblin5150-code/clinical-skills/issues/278)'s
    finding that a proposal's supporting argument can be falsified by the artifact
    it proposes to extend.

    **Both declined forms are implemented here rather than described**, so what
    fails is the rule and not a sentence about it. A taper, a titration, a repeat
    dose and a bolus-then-infusion each put two dose-bearing tokens in one correct
    row. **The conjunction narrowing drops the taper and keeps the other three** --
    it helps and does not close it -- and narrowing past what is left needs a closed
    set of continuation verbs, where a verb missing from that set is a false alarm
    on a correct order: **the same failure
    direction as the drug table
    [#289](https://github.com/mshamblin5150-code/clinical-skills/issues/289)
    prohibits**, which is the ground the ticket rules decision 2's cousins out on.

    **The orders are written here and were not measured against a corpus**, because
    there is none to measure against: a finished draft lives under ``output/`` and
    is written about a patient, which is ``test_reference_scan``'s position exactly.
    So this is a floor -- these forms fire on at least these correct orders -- and
    never a rate.
    """

    DOSE = re.compile(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:mg|mcg|ug|g|kg|mL|ml|L|units?|mEq|IU|%|tablets?|capsules?|puffs?|drops?"
        r"|patch(?:es)?)"
        r"\b(?:\s*/\s*(?:kg|m2|hr|hour|day))?",
        re.I,
    )
    CONJUNCTION = re.compile(r"\band\b|\bplus\b|\s\+\s|\s&\s", re.I)

    # One drug each, every one of them correct as written.
    CORRECT = (
        "Ceftriaxone 1 g IV every 24 hours x 14 days",
        "Doxycycline 100 mg PO BID x 7 days",
        "Amoxicillin-clavulanate 875 mg PO BID x 10 days",
        "Prednisone 40 mg PO daily x 5 days, then 20 mg PO daily x 5 days",
        "Lisinopril 10 mg PO daily, increase to 20 mg after 2 weeks if tolerated",
        "Continued home medication: prenatal vitamin one tablet PO daily",
        "Delayed order: metformin 500 mg PO BID, hold until the acute kidney injury resolves",
        "Insulin glargine 10 units subcutaneously nightly and titrate by 2 units every 3 days",
        "Albuterol 2 puffs inhaled every 4 hours PRN wheeze",
        "Magnesium sulfate 4 g IV over 20 minutes, then 2 g per hour",
        "Ondansetron 4 mg IV once and repeat 4 mg in 8 hours if needed",
        "Normal saline 1 L IV bolus and then 100 mL per hour",
        "Ceftriaxone 1 g IV every 24 hours, continued for the admission",
    )

    # Two drugs welded into one row. The first is the defect the ticket records.
    WELDED = (
        "Doxycycline 100 mg PO BID x 7 days and metronidazole 500 mg PO TID x 7 days",
        "Ceftriaxone 500 mg IM once and azithromycin 1 g PO once",
        "Amoxicillin 500 mg PO TID and clarithromycin 500 mg PO BID x 14 days",
    )

    @classmethod
    def broad(cls, order: str) -> bool:
        """Decision 2 as the ticket words it: a second unit-bearing token."""
        return len(cls.DOSE.findall(order)) >= 2

    @classmethod
    def conjunction(cls, order: str) -> bool:
        """The narrowest form that still catches the recorded defect: a
        conjunction sitting between the first two dose tokens."""
        hits = list(cls.DOSE.finditer(order))
        if len(hits) < 2:
            return False
        return bool(cls.CONJUNCTION.search(order, hits[0].end(), hits[1].start()))

    def test_the_instrument_is_live(self):
        """Both forms catch every welded row, so a clean result below is the rule
        declining to fire and not the rule failing to run. ``TheInstrumentIsLive``
        in ``test_build_artifacts_ignored``, for its reason: most of that class once
        passed against a check that said yes to everything."""
        for order in self.WELDED:
            with self.subTest(order=order):
                self.assertTrue(self.broad(order))
                self.assertTrue(self.conjunction(order))

    def test_the_broad_form_fires_on_correct_orders(self):
        fired = [order for order in self.CORRECT if self.broad(order)]
        self.assertTrue(
            fired,
            "the ticket's decision 2 no longer fires on any correct order here,"
            " so the ruling that declined it needs re-deriving",
        )

    def test_narrowing_to_a_conjunction_still_fires_on_correct_orders(self):
        """The narrowing helps and does not close it, which is the finding: what
        is left is a titration, a repeat dose and an infusion rate, all one drug."""
        fired = [order for order in self.CORRECT if self.conjunction(order)]
        self.assertTrue(
            fired,
            "narrowing to a conjunction now fires on no correct order here, so the"
            " ruling that declined it needs re-deriving",
        )
        self.assertLess(
            len(fired),
            len([order for order in self.CORRECT if self.broad(order)]),
            "the narrowing is supposed to be strictly better than the broad form",
        )

    def a_record_for(self, order: str) -> str:
        """A ledger record naming this order's drug and stating a number.

        Built through the module's own parser, because the drug a record has to
        name is by definition the one the parser read -- whether it reads the
        right one is ``OneDrugRowIsOneDrugAndNothingHereMakesThatTrue``'s
        question, one class up, and not this one's.
        """
        found = ledger.read_prescriptions(rx_table(order))
        drug = found[0].drug if found else "unreadable"
        return a_drug_claim(f"{drug} at 500 mg is the sourced regimen for this indication.")

    def test_the_module_grades_every_one_of_these_orders_clean(self):
        """The ruling asserted against behavior rather than against a spelling.

        **The first version of this asserted the two declined patterns were absent
        from ``research_ledger`` as literal strings**, which any reimplementation
        spelled differently would have passed -- a check that could not fail except
        on verbatim copy-paste, reading as a gate while being none. That is this
        repo's own recurring shape arriving inside the test written to prevent a
        re-proposal, and both axes of ``/code-review`` found it independently.

        What the ruling actually promises is that these orders grade clean, and
        that holds however a future row is written: add either declined form to
        ``prescription_findings`` and this goes red.
        """
        for order in self.CORRECT:
            with self.subTest(order=order):
                self.assertEqual(rx_kinds(rx_table(order), self.a_record_for(order)), [])

    def test_that_clean_list_is_the_rows_declining_and_not_the_harness(self):
        """``TheInstrumentIsLive``'s argument applied to the assertion above.

        Drop the record and every order the sheet does not exempt fires, so a
        clean list up there is the rows finding nothing rather than ``rx_kinds``
        finding nothing to run.
        """
        for order in self.CORRECT:
            if ledger.read_prescriptions(rx_table(order))[0].exempt:
                continue
            with self.subTest(order=order):
                self.assertNotEqual(rx_kinds(rx_table(order)), [])


class TheDeclinedCadenceRowFiresOnCorrectCitations(unittest.TestCase):
    """Why #534 refuses a per-publisher annual-cadence row.

    The declined row is implemented here rather than described: a C.F.R.
    citation whose codification year is behind a later annual codification is
    called stale. The cited sections below are correct in both codifications,
    so every finding is a false alarm about the section's content.

    These citations are written in this test and measured against no corpus.
    The result is therefore a floor on the false-alarm shape and never a rate.
    A finished claim ledger lives under ``scratch/`` and cannot be a fixture.

    This is the historical comparison #534 fixed on 2026-08-27: the official
    2024 and 2025 annual Title 42 codifications, not a claim about which annual
    codification is current whenever the suite happens to run.
    """

    CFR_CODIFICATION_YEAR_PATTERN = re.compile(
        r"\b\d+\s+C\.F\.R\.\s+§+\s+[\d.]+\s+"
        r"\((?P<codification_year>\d{4})\)"
    )
    CORRECT_ACROSS_CODIFICATIONS = (
        (
            "Physicians' services, 42 C.F.R. § 410.20 (2024).",
            "Physicians' services, 42 C.F.R. § 410.20 (2025).",
        ),
        (
            "Condition of participation: Patient's rights, "
            "42 C.F.R. § 482.13 (2024).",
            "Condition of participation: Patient's rights, "
            "42 C.F.R. § 482.13 (2025).",
        ),
        (
            "Resident rights, 42 C.F.R. § 483.10 (2024).",
            "Resident rights, 42 C.F.R. § 483.10 (2025).",
        ),
    )

    @classmethod
    def declined_cadence_row(
        cls, reference: str, later_annual_reference: str
    ) -> bool:
        match = cls.CFR_CODIFICATION_YEAR_PATTERN.search(reference)
        later_match = cls.CFR_CODIFICATION_YEAR_PATTERN.search(
            later_annual_reference
        )
        return bool(
            match
            and later_match
            and int(match.group("codification_year"))
            < int(later_match.group("codification_year"))
        )

    def test_the_instrument_distinguishes_the_later_codification(self):
        later_reference = (
            "Condition of participation: Patient's rights, "
            "42 C.F.R. § 482.13 (2025)."
        )
        self.assertFalse(
            self.declined_cadence_row(later_reference, later_reference)
        )

    def test_the_cadence_row_fires_on_every_correct_citation(self):
        for reference, later_reference in self.CORRECT_ACROSS_CODIFICATIONS:
            with self.subTest(reference=reference):
                self.assertTrue(
                    self.declined_cadence_row(reference, later_reference),
                    "the declined cadence row no longer fires on this correct "
                    "citation, so #534's ruling needs re-deriving",
                )


class CodificationYearProseMatchesTheHistoricalInstrument(
    ProseBind, unittest.TestCase
):
    """#624's bind from the live instructions to #534's fixed comparison."""

    ADR = REPO_ROOT / "docs" / "adr" / (
        "0052-a-codification-year-is-provenance-and-the-snapshot-behind-it-is-"
        "declared-unreached.md"
    )

    @classmethod
    def live_surfaces(cls) -> tuple[Path, ...]:
        return (*ledger_publishing_skills(), Path(ledger.__file__), cls.ADR)

    def test_live_surfaces_use_the_canonical_term(self):
        for path in self.live_surfaces():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertNotRegex(
                    path.read_text(encoding="utf-8").lower(),
                    r"\bedition year\b",
                )

    def test_the_adr_records_the_fixed_historical_comparison(self):
        adr = self.ADR.read_text(encoding="utf-8")
        for moving_current_description in (
            "current annual edition",
            "current annual codification",
        ):
            with self.subTest(description=moving_current_description):
                self.assertProseNotIn(moving_current_description, adr)
        self.assertProseIn(
            "the official 2024 and 2025 annual Title 42 codifications",
            adr,
        )
        self.assertProseIn(
            "not a claim about which annual codification is current whenever "
            "the suite happens to run",
            adr,
        )


# --------------------------------------------------------------------------
# #298 -- the evidence dump cross-references a topic it does not carry
# --------------------------------------------------------------------------

# One topic body, in the shape the rendered dump carries: a title line, then the
# masthead block that opens with ``Authors:``. **Written from the real dump's
# structure rather than invented** -- it carries no headings of any kind, so the
# masthead is the only thing that marks a body as present.
def topic(title: str) -> str:
    return (
        f"{title}\n"
        "Authors: A Author, MD, B Author, MD\n"
        "Section Editors: C Editor, MD\n"
        "Deputy Editor: D Editor, MD\n"
        "Literature review current through: Jul 2026.\n"
        "This topic last updated: Jun 12, 2026.\n"
        "\n"
        "INTRODUCTION\n"
        "Body prose that happens to mention nothing in particular.\n"
    )


def uptodate_entry(title: str, year: str = "2026") -> str:
    """The form [apa7.md](skills/practicum-case-study/reference/apa7.md) §2 publishes."""
    return (
        f"Author, A., & Author, B. ({year}). {title}. UpToDate. Retrieved"
        f" August 20, 2026, from https://www.uptodate.com/contents/some-slug"
    )


def cited(title: str, claim: str = "A claim resting on a topic.") -> str:
    return f"""\
## CLAIM: {claim}
STATUS: sourced
SOURCE: tertiary reference
REFERENCE: {uptodate_entry(title)}
RESTATEMENT: The topic states the thing the claim says it states.
RECENCY: current - the topic was last updated in 2026.
RESOLVED: https://www.uptodate.com/contents/some-slug - read 2026-08-19
PAGE-YEAR: 2026 - stated in the topic's own last-updated line.
REFUTATION: stands - the title and authors match the topic page.
SECOND-ROUTE: topic HTML -> publisher references and author list
STATED-EXPIRY: none stated
"""


class ACarriedTopicIsRecognizedByItsMasthead(unittest.TestCase):
    """The dump carries no headings, so #298 decision 2's *appears as a heading*
    is not implementable against the artifact it was written about. What marks a
    body present is the ``Authors:`` masthead, and the title is the line above it.

    Measured before it was believed: nearly every body the real dump carries
    joins a ``See "..."`` cross-reference exactly under this rule. **The counts
    are #298's to state and are deliberately nowhere in this tree** -- they are
    measured against a file under ``scratch/`` that nothing committed re-derives.
    """

    def test_a_body_is_carried(self):
        self.assertEqual(
            ledger.carried_topics(topic("Pelvic inflammatory disease: Treatment")),
            {"Pelvic inflammatory disease: Treatment"},
        )

    def test_a_cross_reference_is_not_a_body(self):
        """The whole point of the row. A dump refers to far more topics than it
        carries -- by better than an order of magnitude in the real one -- and a
        reference is not a body."""
        text = 'See "Pelvic inflammatory disease: Treatment" for the regimen.\n'
        self.assertEqual(ledger.carried_topics(text), set())

    def test_blank_lines_above_the_masthead_are_skipped(self):
        text = "Some topic title\n\n\nAuthors: A Author, MD\n"
        self.assertEqual(ledger.carried_topics(text), {"Some topic title"})

    def test_two_bodies_are_two_topics(self):
        text = topic("First topic") + "\n" + topic("Second topic")
        self.assertEqual(ledger.carried_topics(text), {"First topic", "Second topic"})

    def test_a_masthead_with_nothing_above_it_names_no_topic(self):
        """A dump opening on the masthead has no title line to read, and an empty
        string in the carried set would match every entry whose title failed to
        parse -- which is a silent pass on the row."""
        self.assertEqual(ledger.carried_topics("Authors: A Author, MD\n"), set())


class AnUpToDateEntryNamesItsTopic(unittest.TestCase):
    """The title element of §2's published form, and nothing looser.

    Scoped to UpToDate because supplied topics belong in the companion evidence;
    opening one through another route does not put it in that set. A journal
    article the dump lacks is
    ``skills/practicum-case-study/SKILL.md`` step 3's ordinary case.
    """

    def test_the_title_element_comes_back(self):
        self.assertEqual(
            ledger.uptodate_topic(uptodate_entry("Pelvic inflammatory disease: Treatment")),
            "Pelvic inflammatory disease: Treatment",
        )

    def test_a_journal_entry_is_not_one(self):
        entry = (
            "Abbassi-Ghanavati, M. (2009). Pregnancy and laboratory studies."
            " Obstetrics and Gynecology, 114(6), 1326-1331."
        )
        self.assertEqual(ledger.uptodate_topic(entry), "")

    def test_the_database_name_is_a_word_and_never_a_hostname(self):
        """``reference_scan``'s recorded defect, adopted rather than rediscovered:
        an entry that drops the database element must not have its title read out
        of ``www.uptodate.com``."""
        entry = (
            "Author, A. (2026). Some topic. Retrieved August 20, 2026, from"
            " https://www.uptodate.com/contents/some-slug"
        )
        self.assertEqual(ledger.uptodate_topic(entry), "")

    def test_an_italicized_database_name_still_reads(self):
        """§2 requires the database name italicized and records that the corpus
        italicizes it nowhere. Both spellings are live, so both read."""
        entry = (
            "Author, A. (2026). Some topic. *UpToDate*. Retrieved August 20, 2026,"
            " from https://www.uptodate.com/contents/x"
        )
        self.assertEqual(ledger.uptodate_topic(entry), "Some topic")

    def test_a_wrapped_entry_reads(self):
        """A ledger's ``REFERENCE`` field wraps onto a hanging indent, and
        ``read_records`` joins it with a single space -- but a caller may hand this
        the raw form."""
        entry = (
            "Author, A. (2026). Pelvic inflammatory disease:\n    Treatment."
            " UpToDate. Retrieved August 20, 2026, from https://x.example/y"
        )
        self.assertEqual(
            ledger.normalize(ledger.uptodate_topic(entry)),
            ledger.normalize("Pelvic inflammatory disease: Treatment"),
        )


class ACitedTopicTheDumpDoesNotCarryIsRefused(unittest.TestCase):
    """#298's ruled row, 2026-08-20.

    **The topics the dump merely refers to are not graded**, and that is the
    ruling rather than an omission: they are the overwhelming majority, their
    reference counts decay smoothly with no plateau anywhere, and any cut on that
    curve is a value named at an edge -- ``SPACE_ADVANCE_FRACTION``'s recorded
    failure and #97's objection. What is graded is the join. **The figures are
    #298's to state**, and this file held the last three after the commit that
    took them out of the other three -- one copy updated and its neighbor left,
    which is the shape ``CLAUDE.md``'s *Console codec* section records.
    """

    def setUp(self):
        self.carried = ledger.carried_topics(topic("A topic the dump carries"))

    def test_a_carried_topic_passes(self):
        records = ledger.read_records(ledger_text(cited("A topic the dump carries")))
        self.assertEqual(ledger.evidence_findings(records, (), self.carried)[0], [])

    def test_an_uncarried_topic_is_a_finding(self):
        records = ledger.read_records(ledger_text(cited("A topic the dump never carried")))
        found, read = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual([f.kind for f in found], [ledger.CITED_TOPIC_NOT_IN_EVIDENCE])
        self.assertEqual(read, 1, "the citation it failed on is a citation it read")

    def test_the_join_ignores_punctuation_and_case(self):
        """``normalize`` and not similarity, on this module's own rule: an entry
        writes the title in sentence case with a trailing period and the topic page
        does not."""
        records = ledger.read_records(cited("a TOPIC the dump carries") and
                                      ledger_text(cited("a TOPIC, the dump carries.")))
        self.assertEqual(ledger.evidence_findings(records, (), self.carried)[0], [])

    def test_a_journal_citation_is_left_alone(self):
        """The scope limb. A source the dump lacks is
        ``skills/practicum-case-study/SKILL.md`` step 3's ordinary case, and
        the row must not fire on it -- that is the direction #215's defect runs in."""
        record = """\
## CLAIM: A claim resting on a journal article.
STATUS: sourced
SOURCE: peer-reviewed
REFERENCE: Abbassi-Ghanavati, M. (2009). Pregnancy and laboratory studies.
    Obstetrics and Gynecology, 114(6), 1326-1331.
RESTATEMENT: The table gives a third-trimester range.
RECENCY: nothing newer - searched 2026-08-19.
RESOLVED: https://doi.org/10.1097/x - read 2026-08-19
PAGE-YEAR: 2009 - on the masthead.
REFUTATION: stands - the volume and pages match.
"""
        records = ledger.read_records(ledger_text(record))
        self.assertEqual(ledger.evidence_findings(records, (), self.carried)[0], [])

    def test_an_unsourced_record_is_left_alone(self):
        """An ``unsourced`` record may carry no ``REFERENCE`` at all -- that is
        ``UNSOURCED_WITH_CITATION_FIELD``'s row -- so there is nothing to join."""
        record = """\
## CLAIM: A claim nothing sourced.
STATUS: unsourced - searched UpToDate, PubMed and the guideline corpus, nothing.
"""
        records = ledger.read_records(ledger_text(record))
        self.assertEqual(ledger.evidence_findings(records, (), self.carried)[0], [])

    def test_a_draft_entry_is_read_too(self):
        """The draft's reference list is where the citation lands, and an entry
        with no ledger record behind it is exactly the #289 shape. The entries come
        from ``reference_scan``'s parser rather than a second one, on
        ``REFERENCE_HEADING``'s precedent and #108's."""
        records = ledger.read_records(ledger_text(cited("A topic the dump carries")))
        entries = (uptodate_entry("A topic nobody handed over"),)
        found, read = ledger.evidence_findings(records, entries, self.carried)
        self.assertEqual([f.kind for f in found], [ledger.CITED_TOPIC_NOT_IN_EVIDENCE])
        self.assertEqual(read, 2, "the record and the entry are both citations")

    def test_one_topic_cited_twice_is_one_finding(self):
        """The row is about a topic, not about a citation of it. Two records
        naming the same missing topic is one thing wrong."""
        records = ledger.read_records(
            ledger_text(cited("A missing topic", "First claim."),
                        cited("A missing topic", "Second claim."))
        )
        found, read = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual(len(found), 1)
        self.assertEqual(read, 2, "one finding, and it is still two citations read")


class AnUpToDateEntryThisCannotReadIsAFinding(unittest.TestCase):
    """``UNREADABLE_DRUG_ROW``'s argument, one row over: a citation this parser
    cannot read is a finding and never a citation subtracted from the set in
    silence.

    **For a gate with no escape hatch, this *was* the hatch.** ``uptodate_topic``
    recognizes a topic only from the database element APA section 2 publishes, so
    an entry that drops ``UpToDate.`` was invisible to the row **and** to the
    population row added to stop a clean zero reading as a checked zero -- and
    ``reference_scan`` reports nothing on it either, so four characters removed
    from an entry took the topic out of the join with nothing red anywhere.

    Found by a tracker-sweep subagent, re-derived in both directions before it was
    believed.
    """

    def setUp(self):
        self.carried = ledger.carried_topics(topic("A carried topic"))

    def entry(self, locator="https://www.uptodate.com/contents/some-slug"):
        """§2's form with the database element dropped -- the recorded shape."""
        return f"Author, A. (2026). Some topic. Retrieved August 20, 2026, from {locator}"

    def test_an_uptodate_locator_with_no_database_element_is_a_finding(self):
        records = ledger.read_records(ledger_text(f"""\
## CLAIM: A claim resting on an entry this cannot read.
STATUS: sourced
SOURCE: tertiary reference
REFERENCE: {self.entry()}
"""))
        found, _ = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual([f.kind for f in found], [ledger.UNREADABLE_UPTODATE_ENTRY])

    def test_it_is_counted_as_a_citation_read(self):
        """The half that matters as much as the finding: it must not vanish from
        the denominator, or the coverage row reports it as checked."""
        records = ledger.read_records(ledger_text(f"""\
## CLAIM: A claim resting on an entry this cannot read.
STATUS: sourced
REFERENCE: {self.entry()}
"""))
        _, read = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual(read, 1)

    def test_a_journal_entry_is_not_one(self):
        """The row is keyed on the **locator's host**, so a source that is not
        UpToDate is left alone exactly as the sibling row leaves it alone."""
        records = ledger.read_records(ledger_text(f"""\
## CLAIM: A claim resting on a journal article.
STATUS: sourced
REFERENCE: {self.entry("https://doi.org/10.1097/AOG.0b013e3181c2bde8")}
"""))
        found, read = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual(found, [])
        self.assertEqual(read, 0)

    def test_a_readable_entry_does_not_fire_it(self):
        """Both rows read the same entry, so the readable one must reach exactly
        one of them -- otherwise a compliant citation is failed twice."""
        records = ledger.read_records(ledger_text(cited("A missing topic")))
        found, _ = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual([f.kind for f in found], [ledger.CITED_TOPIC_NOT_IN_EVIDENCE])

    def test_a_carried_topic_reaches_neither(self):
        records = ledger.read_records(ledger_text(cited("A carried topic")))
        found, read = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual(found, [])
        self.assertEqual(read, 1)

    def test_the_row_is_declared_as_needing_the_flag(self):
        self.assertIn(ledger.UNREADABLE_UPTODATE_ENTRY, ledger.EVIDENCE_ROWS)
        self.assertEqual(ledger.ROWS[ledger.UNREADABLE_UPTODATE_ENTRY], "#298")

    def test_the_host_is_matched_as_a_host_and_not_as_a_word(self):
        """The mirror of the sibling row's guard. Prose naming the database in a
        title must not be read as a locator."""
        records = ledger.read_records(ledger_text("""\
## CLAIM: A claim about a paper discussing UpToDate as a database.
STATUS: sourced
REFERENCE: Author, A. (2026). How clinicians use UpToDate in practice. Journal of
    Medical Informatics, 14(2), 100-110.
"""))
        found, read = ledger.evidence_findings(records, (), self.carried)
        self.assertEqual(found, [])
        self.assertEqual(read, 0)


class TheEvidenceRowsAreWiredInLikeTheDraftRows(unittest.TestCase):
    """#289's arrangement, adopted whole: a row that did not run prints *not
    graded* rather than a zero, on #258's ruling."""

    def test_the_row_is_in_the_vocabulary(self):
        self.assertIn(ledger.CITED_TOPIC_NOT_IN_EVIDENCE, ledger.KINDS)
        self.assertIn(ledger.CITED_TOPIC_NOT_IN_EVIDENCE, ledger.ROWS)
        self.assertEqual(ledger.ROWS[ledger.CITED_TOPIC_NOT_IN_EVIDENCE], "#298")

    def test_the_row_is_declared_as_needing_the_flag(self):
        self.assertIn(ledger.CITED_TOPIC_NOT_IN_EVIDENCE, ledger.EVIDENCE_ROWS)

    def test_every_declared_row_is_a_row(self):
        for kind in ledger.EVIDENCE_ROWS:
            self.assertIn(kind, ledger.KINDS)

    def test_the_report_says_not_graded_without_the_flag(self):
        scan = ledger.survey(ledger.read_records(ledger_text(CLEAN)), AS_OF)
        report = ledger.format_report(scan, source="a.md")
        self.assertIn("evidence topics carried", report)
        self.assertIn("not graded - no --evidence was given", report)
        row = [ln for ln in report.splitlines() if ledger.CITED_TOPIC_NOT_IN_EVIDENCE in ln]
        self.assertEqual(len(row), 1)
        self.assertIn("not graded", row[0])

    def test_the_report_states_the_population_when_it_ran(self):
        """#258's ruling: the run that graded a citation says how many topic
        bodies it had to join against, on the same page as its clean exit."""
        scan = ledger.survey(
            ledger.read_records(ledger_text(CLEAN)),
            AS_OF,
            carried=ledger.carried_topics(topic("A topic")),
        )
        report = ledger.format_report(scan, source="a.md")
        self.assertIn("evidence topics carried          1", report)
        row = [ln for ln in report.splitlines() if ledger.CITED_TOPIC_NOT_IN_EVIDENCE in ln]
        self.assertNotIn("not graded", row[0])


class TheRowSaysHowManyCitationsItRead(unittest.TestCase):
    """#258's ruling one level down, and the gap was found by pointing the command
    at the real ledger rather than by a fixture.

    ``evidence topics carried`` states what the row joined **against**. It says
    nothing about what it joined, so a ledger citing no UpToDate topic at all
    reported ``cited-topic-not-in-evidence 0`` -- indistinguishable from a run
    whose every citation checked out, which is the shape this module already
    refuses twice over.
    """

    def scan(self, *records, carried=None):
        return ledger.survey(
            ledger.read_records(ledger_text(*records)), AS_OF, carried=carried
        )

    def test_a_ledger_citing_no_uptodate_topic_says_so(self):
        report = ledger.format_report(
            self.scan(CLEAN, carried=ledger.carried_topics(topic("A topic"))),
            source="a.md",
        )
        self.assertIn("UpToDate citations read          0", report)

    def test_a_cited_topic_is_counted_whether_or_not_it_is_carried(self):
        """The denominator is what was read, not what failed -- otherwise it is
        the finding count wearing a second name."""
        carried = ledger.carried_topics(topic("A carried topic"))
        scan = self.scan(cited("A carried topic"), cited("A missing topic", "Two."), carried=carried)
        self.assertEqual(scan.uptodate_citations, 2)
        self.assertEqual(scan.evidence_at_fault, 1)

    def test_it_is_not_graded_without_the_flag(self):
        report = ledger.format_report(self.scan(CLEAN), source="a.md")
        self.assertIn("UpToDate citations read", report)
        line = [ln for ln in report.splitlines() if "UpToDate citations read" in ln][0]
        self.assertIn("not graded", line)

    def test_a_journal_citation_is_not_counted(self):
        """The count is the row's population and the row is scoped to UpToDate,
        so counting every reference would overstate what was checked."""
        scan = self.scan(CLEAN, carried=ledger.carried_topics(topic("A topic")))
        self.assertEqual(scan.uptodate_citations, 0)


class TheCommandReadsTheEvidenceFile(unittest.TestCase):
    """End to end, through ``main``, because the flag parsing and the exit status
    are what a run actually meets."""

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            status = ledger.main(argv)
        return status, out.getvalue(), err.getvalue()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name: str, text: str) -> str:
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_a_cited_topic_the_dump_carries_exits_clean(self):
        led = self.write("led.md", ledger_text(cited("A carried topic")))
        ev = self.write("evidence.txt", topic("A carried topic"))
        status, out, _ = self.run_main([led, "--evidence", ev])
        self.assertEqual(status, 0, out)

    def test_a_cited_topic_the_dump_lacks_refuses(self):
        led = self.write("led.md", ledger_text(cited("A topic nobody handed over")))
        ev = self.write("evidence.txt", topic("Some other topic"))
        status, _, err = self.run_main([led, "--evidence", ev])
        self.assertEqual(status, 1)
        self.assertIn("evidence", err.lower())

    def test_an_evidence_file_carrying_no_topic_body_is_exit_2(self):
        """``differential_scan``'s reasoning and the limb that matters most: a
        dump this parser cannot read would otherwise fire the row on every
        citation in the ledger, which is a mass false finding rather than a pass."""
        led = self.write("led.md", ledger_text(cited("A carried topic")))
        ev = self.write("evidence.txt", 'See "A carried topic" for the regimen.\n')
        status, _, err = self.run_main([led, "--evidence", ev])
        self.assertEqual(status, 2)
        self.assertIn("no topic body", err)

    def test_an_unreadable_dump_does_not_suppress_the_other_rows(self):
        """The spec axis's finding, and the one this limb was shipped wrong on.

        Returning 2 at the ``if not carried:`` branch happened **before**
        ``survey``, so a ledger with real #214 findings printed no report at all
        and reported *did not scan*. That is the inversion ``CLAUDE.md`` records
        against ``tracker_scan.py``'s corpus limb, reproduced here.

        Drives ``main`` and not ``format_report``, because every test already
        written for this limb asserted the status and none asserted that the rows
        beneath it survived.
        """
        broken = """\
## CLAIM: A record broken in ways that have nothing to do with the evidence.
STATUS: sourced
SOURCE: not-a-real-class
REFERENCE: Author, A. Something with no year.
RESTATEMENT: A record broken in ways that have nothing to do with the evidence.
"""
        led = self.write("led.md", ledger_text(broken))
        ev = self.write("evidence.txt", 'See "A topic" for the regimen.\n')
        status, out, err = self.run_main([led, "--evidence", ev])
        self.assertEqual(status, 1, "a finding outranks the not-scanned limb")
        self.assertIn("records at fault", out, "the report still prints")
        self.assertIn("no topic body", err, "and the limb still says so")
        self.assertIn("not graded", out, "with the evidence row ungraded")

    def test_an_unreadable_dump_alone_is_exit_2(self):
        """The other half: with nothing else wrong, the deferred status is still
        2, because what did not happen is the scan."""
        led = self.write("led.md", ledger_text(CLEAN))
        ev = self.write("evidence.txt", 'See "A topic" for the regimen.\n')
        status, _, err = self.run_main([led, "--evidence", ev])
        self.assertEqual(status, 2)
        self.assertIn("no topic body", err)

    def test_an_unreadable_dump_does_not_grade_the_row(self):
        """The reason the row is left ungraded rather than run over an empty set:
        with nothing to join against, every UpToDate citation would fire."""
        led = self.write("led.md", ledger_text(cited("A topic nobody handed over")))
        ev = self.write("evidence.txt", 'See "A topic" for the regimen.\n')
        status, out, _ = self.run_main([led, "--evidence", ev])
        self.assertEqual(status, 2, "not 1 - the row did not run, so it found nothing")
        row = [ln for ln in out.splitlines() if ledger.CITED_TOPIC_NOT_IN_EVIDENCE in ln]
        self.assertIn("not graded", row[0])

    def test_a_missing_evidence_file_is_exit_2(self):
        led = self.write("led.md", ledger_text(CLEAN))
        status, _, err = self.run_main([led, "--evidence", str(self.root / "nope.txt")])
        self.assertEqual(status, 2)
        self.assertIn("nope.txt", err)

    def test_the_flag_with_no_value_is_the_usage_line(self):
        """``--draft``'s recorded defect, adopted: without this, ``--evidence
        --show`` reads ``--show`` as the dump and drops the flag besides."""
        led = self.write("led.md", ledger_text(CLEAN))
        status, _, err = self.run_main([led, "--evidence", "--show"])
        self.assertEqual(status, 2)
        self.assertIn("usage:", err)

    def test_the_usage_line_names_the_flag(self):
        self.assertIn("--evidence", ledger.USAGE)

    def test_a_finding_outranks_the_dateless_banner(self):
        """``differential_scan``'s ordering, which this module already follows:
        returning 2 would file the strongest thing known under the weakest
        heading."""
        led = self.write("led.md", ledger_text(cited("A missing topic"), stamp=""))
        ev = self.write("evidence.txt", topic("Some other topic"))
        status, _, _ = self.run_main([led, "--evidence", ev])
        self.assertEqual(status, 1)

    def test_the_report_carries_no_topic_title_without_show(self):
        """The ledger sits under ``scratch/`` and a claim is transcribed from
        faculty material about a patient, so this module's ``--show`` is PHI and
        the default report may not name what a record said."""
        led = self.write("led.md", ledger_text(cited("A topic nobody handed over")))
        ev = self.write("evidence.txt", topic("Some other topic"))
        _, out, _ = self.run_main([led, "--evidence", ev])
        self.assertNotIn("A topic nobody handed over", out)
        _, shown, _ = self.run_main([led, "--evidence", ev, "--show"])
        self.assertIn("A topic nobody handed over", shown)


class TheDraftsReferenceListComesFromTheRendererSideParser(unittest.TestCase):
    """#108's duplication refused at the outset: the draft's reference list is
    parsed by ``reference_scan`` and not by a second reading in here.

    A second parser could put an entry in a different place than the module that
    grades that list does, which is exactly the ``REFERENCE_HEADING`` failure
    ``reference_scan`` records against itself.

    **The identity is the whole guarantee here, and the second test below is not
    #218's second half.** That ticket's lesson applies where two implementations
    survive; sharing the object means none does, so what is left to pin is the
    hand-off rather than the agreement.
    """

    def test_the_entries_come_from_reference_scan(self):
        self.assertIs(ledger.read_document, reference_scan.read_document)

    def test_the_entries_are_what_the_row_is_handed(self):
        """**Not #218's case, and saying so is the point.** There the two modules
        held two parsers and an identity test passed while they still disagreed;
        here the identity above means there is exactly one function, so nothing
        can disagree with it and no second assertion could show that it did.

        What this pins instead is the **hand-off**: that what ``main`` takes off a
        ``Document`` is the entry string ``uptodate_topic`` can read. A rename of
        ``Entry.text``, or a parser that returned entries some other shape, would
        leave the identity test green and this one red."""
        draft = (
            "# A draft\n\nBody prose citing (Author, 2026).\n\n"
            "## References\n\n"
            + uptodate_entry("A topic nobody handed over")
            + "\n"
        )
        document = ledger.read_document(draft)
        self.assertEqual(
            [ledger.uptodate_topic(entry.text) for entry in document.entries],
            ["A topic nobody handed over"],
        )

if __name__ == "__main__":
    unittest.main()
