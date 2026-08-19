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

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from pathlib import Path

import research_ledger as ledger

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "practicum-case-study" / "SKILL.md"

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
        self.assertEqual(kinds(text), [ledger.UNSOURCED_WITH_REFERENCE])

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
        record = replace_field(CLEAN, "REFERENCE", f"Someone, A. ({year}). A study. Journal, 1(1), 1-9.")
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
        """A ledger graded twice, a year apart, has to grade the same both times."""
        text = self._aged(2019, "current")
        self.assertEqual(kinds(text, date(2024, 1, 1)), [])
        self.assertIn(ledger.STALE_UNEXCUSED, kinds(text, date(2026, 1, 1)))

    def test_an_ab_disambiguated_year_still_parses(self):
        """``2019a`` is the form ``reference/apa7.md`` section 3 requires."""
        record = replace_field(
            CLEAN, "REFERENCE", "Someone, A. (2024a). A thing. Journal, 1(1), 1-9."
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
                record = replace_field(record, "REFERENCE", recent)
            with self.subTest(recency=name):
                self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_fifth_disposition_is_a_finding(self):
        record = replace_field(CLEAN, "RECENCY", "probably fine, did not look")
        self.assertIn(ledger.UNKNOWN_RECENCY, kinds(ledger_text(record)))

    def test_a_fifth_disposition_on_an_old_source_also_reports_the_window(self):
        """The two rows are different failures and both are true of that record."""
        record = replace_field(CLEAN, "REFERENCE", "Someone, A. (2011). A study. Journal, 1(1), 1-9.")
        record = replace_field(record, "RECENCY", "probably fine")
        found = kinds(ledger_text(record))
        self.assertIn(ledger.UNKNOWN_RECENCY, found)
        self.assertIn(ledger.STALE_UNEXCUSED, found)

    def test_a_missing_recency_reports_the_missing_field_and_not_a_fifth_word(self):
        found = kinds(ledger_text(replace_field(CLEAN, "RECENCY", None)))
        self.assertIn(ledger.MISSING_FIELD, found)
        self.assertNotIn(ledger.UNKNOWN_RECENCY, found)


class TheWindowIsTheOneRowADatelessLedgerLoses(unittest.TestCase):
    def test_an_old_source_is_not_reported_without_a_date_to_measure_against(self):
        record = replace_field(CLEAN, "REFERENCE", "Someone, A. (2011). A study. Journal, 1(1), 1-9.")
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
        record = replace_field(CLEAN, "REFERENCE", self.UNDATED)
        record = replace_field(record, "RECENCY", "current")
        self.assertIn(ledger.UNDATED_REFERENCE, kinds(ledger_text(record)))

    def test_n_d_with_an_excuse_and_a_reason_stands(self):
        record = replace_field(CLEAN, "REFERENCE", self.UNDATED)
        record = replace_field(
            record, "RECENCY", "nothing newer - the page states no revision date and CDC issues none."
        )
        self.assertEqual(kinds(ledger_text(record)), [])

    def test_a_bare_excuse_does_not_buy_the_hatch(self):
        """Otherwise ``nothing newer`` alone would clear two rows at once."""
        record = replace_field(CLEAN, "REFERENCE", self.UNDATED)
        record = replace_field(record, "RECENCY", "nothing newer")
        found = kinds(ledger_text(record))
        self.assertIn(ledger.BARE_EXCUSE, found)
        self.assertIn(ledger.UNDATED_REFERENCE, found)

    def test_a_missing_reference_reports_the_missing_field_and_not_the_year(self):
        found = kinds(ledger_text(replace_field(CLEAN, "REFERENCE", None)))
        self.assertIn(ledger.MISSING_FIELD, found)
        self.assertNotIn(ledger.UNDATED_REFERENCE, found)


class TheReportCarriesNoClaimTextWithoutShow(unittest.TestCase):
    def setUp(self):
        record = replace_field(CLEAN, "SOURCE", "a blog post")
        self.scan = ledger.survey(ledger.read_records(ledger_text(record)), AS_OF)

    def test_the_default_report_prints_no_claim_and_no_field(self):
        report = ledger.format_report(self.scan, source="case-study-claims.md")
        self.assertNotIn("white count", report)
        self.assertNotIn("a blog post", report)

    def test_show_prints_them(self):
        report = ledger.format_report(self.scan, source="case-study-claims.md", show=True)
        self.assertIn("white count", report)
        self.assertIn("a blog post", report)

    def test_every_row_is_named_in_the_report_with_its_ticket(self):
        report = ledger.format_report(self.scan, source="case-study-claims.md")
        for kind in ledger.KINDS:
            with self.subTest(row=kind):
                self.assertIn(f"{ledger.ROW_TICKET[kind]} - {kind}", report)


class TheCommandExitsOnWhatItFound(unittest.TestCase):
    def _run(self, text: str, name: str = "case-study-claims.md") -> int:
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
            path = Path(temp) / "case-study-claims.md"
            path.write_text(
                ledger_text(replace_field(CLEAN, "SOURCE", "a blog post"), stamp=""),
                encoding="utf-8",
            )
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                ledger.main([str(path)])
        self.assertIn("no DATE:", err.getvalue())
        self.assertIn("NO DATE HEADER", out.getvalue())

    def test_a_dateless_ledger_still_grades_the_nine_rows_that_do_not_need_it(self):
        text = ledger_text(replace_field(CLEAN, "SOURCE", "a blog post"), stamp="")
        self.assertEqual(kinds(text, None), [ledger.UNKNOWN_SOURCE_CLASS])

    def test_the_exit_one_message_names_no_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "case-study-claims.md"
            path.write_text(ledger_text(replace_field(CLEAN, "SOURCE", "a blog post")), encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                ledger.main([str(path)])
        self.assertNotIn("white count", out.getvalue() + err.getvalue())


class TheSkillSaysWhatThisChecks(unittest.TestCase):
    """``test_spelling_scan``'s rule: a scanner that has drifted from the file a
    reader opens is worse than none, because it reads as agreement."""

    @classmethod
    def setUpClass(cls):
        cls.skill = SKILL.read_text(encoding="utf-8")

    def test_the_skill_names_the_command(self):
        self.assertIn("python tools/research_ledger.py scratch/case-study-claims.md", self.skill)

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
        ledger.MISSING_FIELD: "a field missing or empty",
        ledger.UNKNOWN_STATUS: "a `STATUS` that is neither word",
        ledger.BARE_STATUS: "an `unsourced` with nothing said about what was searched",
        ledger.UNSOURCED_WITH_REFERENCE: "an `unsourced` record carrying a `REFERENCE`",
        ledger.UNKNOWN_SOURCE_CLASS: "a `SOURCE` outside the four",
        ledger.UNKNOWN_RECENCY: "a `RECENCY` outside the four",
        ledger.RESTATEMENT_ECHOES_CLAIM: "a `RESTATEMENT` that is the claim pasted back",
        ledger.NUMERIC_CLAIM_UNQUANTIFIED: "whose restatement carries none",
        ledger.UNDATED_REFERENCE: "a reference stating no year",
        ledger.STALE_UNEXCUSED: "more than five years before `DATE` with no excuse",
        ledger.BARE_EXCUSE: "an excuse with no reason after it",
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

    def test_the_skill_carries_the_amended_recency_rule_and_not_the_retired_one(self):
        """#215's correction. The retired version cut a correct claim for being
        old, and a run reading it would cut one again."""
        self.assertIn("stands where nothing newer exists", self.skill)
        self.assertNotIn("five years the outside limit", self.skill)
        self.assertNotIn("written as historical or dropped", self.skill)

    def test_the_skill_writes_down_the_fallback_for_a_harness_without_subagents(self):
        """#214's open question 1, and #218 takes the same answer."""
        self.assertIn("no subagent tool", self.skill)
        self.assertIn("one at a time in the main\ncontext", self.skill)

    def test_the_skill_says_a_clean_scan_is_not_a_checked_claim(self):
        self.assertIn("A clean scan is not a checked claim", self.skill)

    def test_the_skill_sends_the_ledger_to_a_gitignored_directory(self):
        self.assertIn("scratch/case-study-claims.md", self.skill)
        self.assertNotIn("output/case-study-claims.md", self.skill)

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
        """The fenced block in step 3 that shows a record.

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


if __name__ == "__main__":
    unittest.main()
