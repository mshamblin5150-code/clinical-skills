"""Cover ``specificity_scan``'s parser against synthetic worksheets.

Every worksheet here is written in this file, the way ``test_skills_mirror``
builds throwaway checkouts rather than touching the real one.

**That used to be because no committed run of ``icd10-cpt`` existed. One does
now** -- ``fixtures/filled-anchor/run-2/``, from [#124] -- and the fixtures stay
invented anyway, on ``test_icd10.py``'s reasoning: a test reading the run this
scanner's own row graded would pass for two reasons, one of them being that the
run and the scanner are wrong together.

``TheSkillSaysWhatThisChecks`` is the one test that reads a committed file, and
it is there for ``test_spelling_scan``'s reason: a scanner that drifts from the
file a reader opens is worse than no scanner, because it reads as agreement.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

import specificity_scan as scan
from icd10_lookup import describe, normalize, notes_for, open_database

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL = REPO_ROOT / "skills" / "icd10-cpt" / "SKILL.md"
NOTES = REPO_ROOT / "fixtures" / "filled-anchor" / "notes"

# The audit's extraction boundary, written down rather than described. A
# diagnosis-list header runs to the next blank line; six of the twelve notes
# bold the header and six do not, and a matcher requiring the bold markers
# silently reads half the set -- which is how the first version of this audit
# published 52 where the answer is 106.
DIAGNOSIS_HEADER = re.compile(
    r"(?i)^\**\s*(?:Preexisting diagnoses \(ICD10\)|Final diagnosis)\s*\**\s*:"
)
CODE_TOKEN = re.compile(r"\b([A-TV-Z][0-9][0-9A-Z](?:\.[0-9A-Z]{1,4})?)\b")


def diagnosis_list_codes(text: str) -> set[str]:
    """Every code-shaped token in a note's two diagnosis-list paragraphs."""
    codes: set[str] = set()
    inside = False
    for line in text.splitlines():
        if DIAGNOSIS_HEADER.match(line):
            inside = True
            codes.update(CODE_TOKEN.findall(line))
        elif inside and line.strip():
            codes.update(CODE_TOKEN.findall(line))
        else:
            inside = False
    return codes


def worksheet(*entries: str) -> str:
    return "--- PROPOSED CODES ---\n\n" + "\n\n".join(entries) + "\n"


def entry(code: str, descriptor: str, specificity: str) -> str:
    return (
        f"ICD-10  {code}  {descriptor}\n"
        f'  ANCHOR: "the note text"\n'
        f"  SPECIFICITY: {specificity}\n"
        f"  CONFIDENCE: verified against ICD-10-CM FY2026"
    )


def second_read(*codes: dict) -> dict:
    return {"read_on": "2026-08-20", "codes": list(codes)}


def read_code(
    code: str,
    *,
    about: str = "the code set leaves no further axis beneath this code",
    family: list[dict] | None = None,
) -> dict:
    return {
        "code": code,
        "family": family or [],
        "about": about,
    }


def fact(
    code: str,
    descriptor: str,
    *,
    billable: bool = True,
    notes: list[dict] | None = None,
) -> dict:
    return {
        "code": code,
        "descriptor": descriptor,
        "billable": billable,
        "notes": notes or [],
    }


Z90_NOTES = [
    {
        "code": "Z90",
        "kind": "excludes1",
        "text": "congenital absence - see Alphabetical Index",
    },
    {
        "code": "Z90",
        "kind": "excludes2",
        "text": "postprocedural absence of endocrine glands (E89.-)",
    },
]


def release_family(code: str) -> list[dict]:
    """The shipped category facts, used to make a record before planting one defect."""
    connection = open_database()
    try:
        category = normalize(code)[:3]
        codes = [
            row[0]
            for row in connection.execute(
                "SELECT code FROM code WHERE code LIKE ? ORDER BY code", (category + "%",)
            )
        ]
        family: list[dict] = []
        for family_code in codes:
            official = describe(connection, family_code)
            family.append(
                fact(
                    family_code,
                    official.long,
                    billable=official.billable,
                    notes=[
                        {"code": note.code, "kind": note.kind, "text": note.text}
                        for note in notes_for(connection, family_code)
                    ],
                )
            )
        return family
    finally:
        connection.close()


class TheParserPairsAFlagWithItsDescriptor(unittest.TestCase):
    def test_it_reads_the_code_and_descriptor_above_the_flag(self):
        flags = scan.read_flags(entry("R12", "Heartburn", "complete — R12 has no further axis"))
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0].code, "R12")
        self.assertEqual(flags[0].descriptor, "Heartburn")
        self.assertEqual(flags[0].keyword, "complete")

    def test_a_wrapped_descriptor_keeps_its_not_for_entry_exemption(self):
        # The mark lands on the continuation line when the official descriptor runs
        # past one. Reading only the code's own line calls this for-entry and then
        # would count it in the ``unspecified`` advisory without the exemption,
        # even though a differential is coded at that level on purpose.
        wrapped = (
            "ICD-10  K27.9  Peptic ulcer, site unspecified, unspecified as acute or chronic,"
            " without\n"
            "               hemorrhage or perforation   NOT FOR ENTRY\n"
            "  SPECIFICITY: complete — nothing further\n"
        )
        flags = scan.read_flags(wrapped)
        self.assertEqual(len(flags), 1)
        self.assertFalse(flags[0].for_entry)
        self.assertEqual(scan.findings(flags), [])

    def test_a_differential_entry_carries_no_flag_and_is_not_graded(self):
        differential = (
            "--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---\n"
            "ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY\n"
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n"
        )
        self.assertEqual(scan.read_flags(differential), [])

    def test_a_cpt_entry_after_the_differential_pairs_with_its_own_header(self):
        """`CPT` opens an entry, so the differential above it never claims the flag."""
        text = (
            "--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---\n"
            "ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY\n"
            "  CONFIDENCE: verified against ICD-10-CM FY2026\n"
            "\n"
            "CPT  10060  Incision and drainage of abscess; simple or single\n"
            "  SPECIFICITY: complete — simple single abscess, documented\n"
        )
        flags = scan.read_flags(text)
        self.assertEqual([f.code for f in flags], ["10060"])
        self.assertEqual(scan.findings(flags), [])

    def test_a_differential_flag_is_exempt_from_both_tests(self):
        """A differential is coded at the unspecified level on purpose.

        Writing a `SPECIFICITY` line there is a C4 failure — the part count — and
        grading it under C5 would fail a descriptor the skill itself asked for.
        """
        text = (
            "ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY\n"
            "  SPECIFICITY: complete\n"
        )
        flags = scan.read_flags(text)
        self.assertFalse(flags[0].for_entry)
        self.assertEqual(scan.findings(flags), [])
        self.assertEqual(scan.survey([flags]).not_for_entry_flags, 1)

    def test_a_cpt_entry_is_read_the_same_way(self):
        text = (
            "CPT  10060  Incision and drainage of abscess\n"
            "  SPECIFICITY: complete — the note documents a simple single abscess\n"
        )
        flags = scan.read_flags(text)
        self.assertEqual([f.code for f in flags], ["10060"])

    def test_a_flag_with_no_entry_above_it_still_parses(self):
        flags = scan.read_flags("  SPECIFICITY: complete\n")
        self.assertEqual(flags[0].descriptor, "")
        self.assertEqual(flags[0].code, "")


class AFlagCarriesSubstanceBeyondItsKeyword(unittest.TestCase):
    """C5's enforced test reaches both branches."""

    def test_a_bare_complete_fails(self):
        flags = scan.read_flags(entry("Z98.51", "Tubal ligation status", "complete"))
        self.assertEqual([f.kind for f in scan.findings(flags)], ["bare-flag"])

    def test_a_complete_with_a_reason_passes(self):
        text = entry("Z98.51", "Tubal ligation status", "complete — Z98.51 has no further axis")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_punctuation_alone_is_not_a_reason(self):
        flags = scan.read_flags(entry("R12", "Heartburn", "complete."))
        self.assertEqual([f.kind for f in scan.findings(flags)], ["bare-flag"])

    def test_a_reason_without_a_dash_passes(self):
        text = entry("K80.20", "Calculus of gallbladder", "complete for this axis, no status code exists")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_a_bare_needs_fails_on_the_same_test(self):
        flags = scan.read_flags(entry("S61.401A", "Unspecified open wound of right hand", "needs:"))
        kinds = [f.kind for f in scan.findings(flags)]
        self.assertIn("bare-flag", kinds)

    def test_a_needs_naming_an_axis_passes(self):
        text = entry("M79.10", "Myalgia, unspecified site", "needs: site")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])


class AnUnspecifiedDescriptorIsAnAdvisoryReviewShape(unittest.TestCase):
    """The descriptor is counted for a reader, but a reason discharges C5."""

    def test_the_ticket_135_bradycardia_reason_discharges_c5(self):
        text = entry(
            "R00.1",
            "Bradycardia, unspecified",
            "complete — R00.1 is the only bradycardia code",
        )
        flags = scan.read_flags(text)
        self.assertEqual(scan.findings(flags), [])
        survey = scan.survey([flags])
        self.assertEqual(survey.unspecified_complete, 1)
        self.assertEqual([f.kind for f in survey.advisories], ["unspecified-complete"])

    def test_the_ticket_135_diarrhea_reason_discharges_c5(self):
        text = entry(
            "R19.7",
            "Diarrhea, unspecified",
            "complete — R19.7 has no sibling naming a more specific diarrhea",
        )
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_the_same_descriptor_passes_with_needs(self):
        text = entry("M19.90", "Unspecified osteoarthritis, unspecified site", "needs: site")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_not_specified_is_counted_for_review_too(self):
        text = entry("N39.0", "Urinary tract infection, site not specified", "complete — no axis remains")
        flags = scan.read_flags(text)
        self.assertEqual(scan.findings(flags), [])
        self.assertEqual(scan.survey([flags]).unspecified_complete, 1)

    def test_an_other_residual_is_not_an_unspecified_one(self):
        """``R06.89`` says the finding fits no named code, not that the note is thin."""
        text = entry("R06.89", "Other abnormalities of breathing", "complete — R06.89 is the residual")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_other_specified_is_not_not_specified(self):
        text = entry("R79.89", "Other specified abnormal findings of blood chemistry", "complete — residual")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_a_bare_complete_still_fails_and_is_counted_for_review(self):
        flags = scan.read_flags(entry("J02.9", "Acute pharyngitis, unspecified", "complete"))
        self.assertEqual([f.kind for f in scan.findings(flags)], ["bare-flag"])
        self.assertEqual(scan.survey([flags]).unspecified_complete, 1)


class TheReportCarriesNoTextWithoutShow(unittest.TestCase):
    """A run directory is a patient record; the default output is pasteable."""

    def setUp(self):
        self.flags = scan.read_flags(
            worksheet(
                entry("M19.90", "Unspecified osteoarthritis, unspecified site", "complete"),
                entry("I10", "Essential (primary) hypertension", "complete — I10 has no further axis"),
            )
        )
        self.survey = scan.survey([self.flags])

    def test_the_counts_are_right(self):
        self.assertEqual(self.survey.worksheets, 1)
        self.assertEqual(self.survey.flags, 2)
        self.assertEqual(self.survey.complete_flags, 2)
        self.assertEqual(self.survey.bare_flags, 1)
        self.assertEqual(self.survey.unspecified_complete, 1)

    def test_the_advisory_count_does_not_add_a_failure(self):
        self.assertEqual(self.survey.failing_flags, 1)
        self.assertEqual(len(self.survey.findings), 1)

    def test_no_descriptor_reaches_the_default_report(self):
        report = scan.format_report(self.survey, source="a-run", show=False)
        self.assertNotIn("osteoarthritis", report)
        self.assertNotIn("hypertension", report)
        self.assertNotIn("M19.90", report)

    def test_show_names_the_code_and_the_flag(self):
        report = scan.format_report(self.survey, source="a-run", show=True)
        self.assertIn("M19.90", report)
        self.assertIn("bare-flag", report)
        self.assertIn("unspecified-complete", report)

    def test_the_unspecified_count_is_labeled_advisory(self):
        report = scan.format_report(self.survey, source="a-run", show=False)
        self.assertIn("advisory - complete on unspecified", report)

    def test_show_names_advisory_flags_for_reader_review(self):
        flags = scan.read_flags(
            entry(
                "R00.1",
                "Bradycardia, unspecified",
                "complete — R00.1 is the only bradycardia code",
            )
        )
        report = scan.format_report(scan.survey([flags]), source="a-run", show=True)
        self.assertIn("R00.1", report)
        self.assertIn("unspecified-complete", report)


class TheCommandExitsOnWhatItFound(unittest.TestCase):
    def _run(self, *entries: str) -> int:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "case-01.md").write_text(worksheet(*entries), encoding="utf-8")
            return scan.main([str(directory)])

    def test_a_clean_run_exits_zero(self):
        self.assertEqual(self._run(entry("I10", "Essential (primary) hypertension", "complete — no further axis")), 0)

    def test_a_bare_flag_exits_one(self):
        self.assertEqual(self._run(entry("I10", "Essential (primary) hypertension", "complete")), 1)

    def test_a_missing_directory_exits_two_rather_than_one(self):
        """Not having scanned is a different answer from having found nothing."""
        self.assertEqual(scan.main(["no-such-directory-here"]), 2)

    def test_no_arguments_exits_two(self):
        self.assertEqual(scan.main([]), 2)

    def test_a_directory_with_no_worksheets_exits_two(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(scan.main([temp]), 2)

    def test_a_readme_is_not_counted_as_a_worksheet(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "README.md").write_text("prose about the run\n", encoding="utf-8")
            self.assertEqual(scan.main([str(directory)]), 2)


class TheIndependentReadBriefCarriesNoAnswer(unittest.TestCase):
    """The reader gets locators, never the worksheet's answer or its prose."""

    def test_it_lists_each_for_entry_icd10_code_once(self):
        text = worksheet(
            entry("Z90.49", "Acquired absence of other specified parts", "complete — leaf"),
            entry("Z90.49", "Acquired absence of other specified parts", "complete — leaf"),
            entry("I10", "Essential hypertension", "complete — no axis"),
        )
        brief = scan.brief([scan.read_flags(text)], source="a-run")
        self.assertEqual(brief.count("Z90.49"), 1)
        self.assertEqual(brief.count("I10"), 1)

    def test_it_exposes_neither_descriptor_nor_existing_reason(self):
        text = entry(
            "Z90.49",
            "Acquired absence of other specified parts of digestive tract",
            "complete — the author's conclusion must stay hidden",
        )
        brief = scan.brief([scan.read_flags(text)], source="a-run")
        self.assertNotIn("Acquired absence", brief)
        self.assertNotIn("author's conclusion", brief)

    def test_it_excludes_cpt_and_not_for_entry_codes(self):
        text = (
            "ICD-10  J20.9  Acute bronchitis, unspecified   NOT FOR ENTRY\n"
            "  SPECIFICITY: complete — differential\n\n"
            "CPT  10060  Incision and drainage of abscess\n"
            "  SPECIFICITY: complete — simple single abscess\n\n"
            + entry("I10", "Essential hypertension", "complete — no axis")
        )
        brief = scan.brief([scan.read_flags(text)], source="a-run")
        self.assertIn("I10", brief)
        self.assertNotIn("J20.9", brief)
        self.assertNotIn("10060", brief)

    def test_it_states_the_record_shape_and_the_independence_caveat(self):
        brief = scan.brief(
            [scan.read_flags(entry("I10", "Essential hypertension", "complete — no axis"))],
            source="a-run",
        )
        for field in scan.SECOND_READ_CODE_FIELDS:
            self.assertIn(f'"{field}"', brief)
        self.assertIn('"read_on"', brief)
        self.assertIn("smoke test", brief.lower())
        self.assertIn("Do not consult", brief)

    def test_a_for_entry_code_with_no_specificity_line_still_enters_the_brief(self):
        text = "ICD-10  I10  Essential (primary) hypertension\n  ANCHOR: the note text\n"
        brief = scan.brief([scan.read_entries(text)], source="a-run")
        self.assertIn("I10", brief)


class TheSecondReadIsBoundToTheCommittedRelease(unittest.TestCase):
    def setUp(self):
        self.flags = [
            scan.read_flags(
                entry(
                    "Z90.49",
                    "Acquired absence of other specified parts of digestive tract",
                    "complete — Z90.4 has only a pancreas child",
                )
            )
        ]
        self.connection = open_database()
        self.addCleanup(self.connection.close)

    def _read(self, *codes: dict) -> scan.SecondRead:
        return scan.load_second_read_record(second_read(*codes), Path("read.json"))

    def _subject(self, **changes) -> dict:
        record = read_code(
            "Z90.49",
            family=release_family("Z90.49"),
            about="stomach is a sibling family and Z90.49 is the digestive residual",
        )
        record.update(changes)
        return record

    def _with_family_change(self, code: str, **changes) -> dict:
        record = json.loads(json.dumps(self._subject()))
        target = next(fact for fact in record["family"] if normalize(fact["code"]) == normalize(code))
        target.update(changes)
        return record

    def test_exact_release_facts_are_clean_and_the_prose_is_paired(self):
        result = scan.gate_second_read(
            self.flags, self._read(self._subject()), self.connection
        )
        self.assertEqual(result.refusals, ())
        self.assertEqual(result.uncovered, ())
        self.assertEqual(len(result.pairings), 1)
        self.assertIn("only a pancreas child", result.pairings[0])
        self.assertIn("stomach is a sibling family", result.pairings[0])

    def test_a_false_subject_descriptor_refuses(self):
        result = scan.gate_second_read(
            self.flags,
            self._read(
                self._with_family_change(
                    "Z90.49", descriptor="Acquired absence of large intestine"
                )
            ),
            self.connection,
        )
        self.assertEqual(len(result.refusals), 1)
        self.assertIn("descriptor", result.refusals[0])

    def test_a_false_supporting_fact_refuses(self):
        result = scan.gate_second_read(
            self.flags,
            self._read(
                self._with_family_change(
                    "Z90.3", descriptor="Acquired absence of large intestine"
                )
            ),
            self.connection,
        )
        self.assertEqual(len(result.refusals), 1)
        self.assertIn("family", result.refusals[0])

    def test_an_incomplete_note_set_refuses(self):
        result = scan.gate_second_read(
            self.flags,
            self._read(self._with_family_change("Z90.49", notes=[])),
            self.connection,
        )
        self.assertEqual(len(result.refusals), 1)
        self.assertIn("notes", result.refusals[0])

    def test_an_omitted_family_member_refuses(self):
        record = self._subject()
        record["family"] = [
            fact for fact in record["family"] if normalize(fact["code"]) != "Z903"
        ]
        result = scan.gate_second_read(
            self.flags, self._read(record), self.connection
        )
        self.assertEqual(len(result.refusals), 1)
        self.assertIn("family coverage", result.refusals[0])

    def test_an_empty_family_is_not_a_read(self):
        loaded = self._read(read_code("Z90.49", family=[]))
        self.assertFalse(loaded.ok)
        self.assertIn("non-empty", loaded.why_not)

    def test_a_subject_not_present_in_its_recorded_family_refuses(self):
        record = self._subject(code="Z90.99")
        result = scan.gate_second_read(
            self.flags, self._read(record), self.connection
        )
        self.assertTrue(any("not in ICD-10-CM" in refusal for refusal in result.refusals))

    def test_a_subject_the_read_omits_is_uncovered_not_agreement(self):
        result = scan.gate_second_read(
            self.flags,
            self._read(),
            self.connection,
            entries=[scan.read_entries(entry("Z90.49", "descriptor", "complete — reason"))],
        )
        self.assertEqual(result.refusals, ())
        self.assertEqual(result.uncovered, ("Z90.49",))
        self.assertEqual(result.pairings, ())

    def test_a_well_formed_record_requires_every_field_and_a_date(self):
        missing_date = scan.load_second_read_record({"codes": []}, Path("read.json"))
        self.assertFalse(missing_date.ok)
        for field_name in scan.SECOND_READ_CODE_FIELDS:
            record = self._subject()
            del record[field_name]
            loaded = self._read(record)
            self.assertFalse(loaded.ok, field_name)


class TheCommandGradesTheSeparatedRead(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        self.run = self.root / "run"
        self.run.mkdir()
        (self.run / "case-01.md").write_text(
            worksheet(
                entry(
                    "Z90.49",
                    "Acquired absence of other specified parts of digestive tract",
                    "complete — the original reason",
                )
            ),
            encoding="utf-8",
        )
        self.read_path = self.root / "read.json"

    def _record(self, **changes) -> dict:
        record = read_code(
            "Z90.49",
            family=release_family("Z90.49"),
            about="the independent account",
        )
        record.update(changes)
        return second_read(record)

    def _run(self, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = scan.main([str(self.run), *extra])
        return status, out.getvalue(), err.getvalue()

    def _write(self, record: object) -> None:
        self.read_path.write_text(json.dumps(record), encoding="utf-8")

    def test_brief_prints_the_locator_and_warns_that_it_is_sensitive(self):
        status, printed, errors = self._run("--brief")
        self.assertEqual(status, 0)
        self.assertIn("Z90.49", printed)
        self.assertIn("PHI", errors)

    def test_a_complete_clean_read_exits_zero_and_prints_the_caveat(self):
        self._write(self._record())
        status, printed, _ = self._run("--second-read", str(self.read_path))
        self.assertEqual(status, 0)
        self.assertIn(scan.SECOND_READ_IS_A_SMOKE_TEST, printed)
        self.assertIn("source fact(s) at fault         0", printed)

    def test_default_output_carries_no_reason_or_independent_prose(self):
        self._write(self._record())
        _, printed, _ = self._run("--second-read", str(self.read_path))
        self.assertNotIn("original reason", printed)
        self.assertNotIn("independent account", printed)

    def test_show_prints_the_ungraded_pairing(self):
        self._write(self._record())
        _, printed, _ = self._run("--second-read", str(self.read_path), "--show")
        self.assertIn("original reason", printed)
        self.assertIn("independent account", printed)
        self.assertIn("UNGRADED", printed)

    def test_a_false_release_fact_exits_one(self):
        record = self._record()
        subject = next(
            fact for fact in record["codes"][0]["family"] if normalize(fact["code"]) == "Z9049"
        )
        subject["descriptor"] = "Acquired absence of large intestine"
        self._write(record)
        status, _, errors = self._run("--second-read", str(self.read_path))
        self.assertEqual(status, 1)
        self.assertIn("source fact", errors)

    def test_an_uncovered_code_exits_two_and_never_reads_as_agreement(self):
        self._write(second_read())
        status, printed, _ = self._run("--second-read", str(self.read_path))
        self.assertEqual(status, 2)
        self.assertIn("NOT COMPLETE", printed)
        self.assertNotIn(scan.SECOND_READ_IS_A_SMOKE_TEST, printed)

    def test_an_invalid_record_exits_two(self):
        self._write({"codes": []})
        status, _, errors = self._run("--second-read", str(self.read_path))
        self.assertEqual(status, 2)
        self.assertIn("not graded", errors)

    def test_a_missing_record_never_prints_its_sensitive_parent_path(self):
        missing = self.root / "2026-08-20-sensitive-site" / "read.json"
        status, _, errors = self._run("--second-read", str(missing))
        self.assertEqual(status, 2)
        self.assertIn("read.json", errors)
        self.assertNotIn("2026-08-20-sensitive-site", errors)

    def test_a_code_without_a_specificity_line_cannot_vanish_from_coverage(self):
        (self.run / "case-01.md").write_text(
            "ICD-10  I10  Essential (primary) hypertension\n  ANCHOR: the note text\n",
            encoding="utf-8",
        )
        self._write(second_read())
        status, printed, _ = self._run("--second-read", str(self.read_path))
        self.assertEqual(status, 2)
        self.assertIn("subject code(s) uncovered       1", printed)


class TheAuditFiguresAreReDerivable(unittest.TestCase):
    """Pin the figures #56 rests on, the way ``test_filled_vitals_census`` does.

    C5's second limb is justified by a count over the committed inputs, and run 1's
    output no longer exists to check it against — so this count is the whole of the
    evidence. **A figure that can only be cited is a weaker thing than one that can
    be recomputed**, which is the standard the skill file states in its own prose,
    and this class is that standard applied to the figure the prose quotes.

    It reads the shipped database, which ``test_icd10`` deliberately does not. The
    prohibition there is against circularity — a parser tested on the file its own
    builder wrote — and there is none here: the database is the reference, not the
    thing under test. ``scan.UNSPECIFIED`` is imported rather than restated, so the
    audit and the scanner cannot come to disagree about what the word means.
    """

    @classmethod
    def setUpClass(cls):
        cls.notes = sorted(NOTES.glob("case-*.md"))
        cls.codes = sorted(
            {
                code
                for note in cls.notes
                for code in diagnosis_list_codes(note.read_text(encoding="utf-8"))
            }
        )
        connection = open_database()
        try:
            cls.resolved = {
                code: connection.execute(
                    "SELECT code, billable, long FROM code WHERE code = ?",
                    (normalize(code),),
                ).fetchone()
                for code in cls.codes
            }
            cls.children = {
                code: connection.execute(
                    "SELECT count(*) FROM code WHERE code LIKE ? AND code != ?",
                    (row[0] + "%", row[0]),
                ).fetchone()[0]
                for code, row in cls.resolved.items()
                if row
            }
        finally:
            connection.close()

    def test_it_reads_all_twelve_notes(self):
        self.assertEqual(len(self.notes), 12)

    def test_the_universe_is_106_distinct_codes(self):
        self.assertEqual(len(self.codes), 106)

    def test_every_one_of_them_resolves(self):
        self.assertEqual([c for c, row in self.resolved.items() if row is None], [])

    def test_23_carry_unspecified_in_their_official_descriptor(self):
        vague = [c for c, row in self.resolved.items() if scan.UNSPECIFIED.search(row[2])]
        self.assertEqual(len(vague), 23)

    def test_105_of_the_106_are_leaves(self):
        self.assertEqual(sum(1 for n in self.children.values() if n == 0), 105)

    def test_the_one_non_leaf_is_a_prose_mention_rather_than_a_proposed_code(self):
        """``E11`` is named in a list's own explanatory aside; ``E11.9`` is the code.

        This is the extraction's one known false positive and it is pinned rather
        than filtered — a boundary that dropped it would need a rule for telling a
        proposed code from a code the prose discusses, which is a reader's job.
        """
        non_leaves = [c for c, n in self.children.items() if n]
        self.assertEqual(non_leaves, ["E11"])
        self.assertFalse(self.resolved["E11"][1], "E11 is a header, not billable")
        self.assertIn("E11.9", self.codes)


class TheSkillSaysWhatThisChecks(unittest.TestCase):
    """The scanner may not hold a different answer than ``icd10-cpt`` does."""

    def setUp(self):
        self.skill = SKILL.read_text(encoding="utf-8")

    def test_the_template_requires_a_reason_beside_complete(self):
        self.assertIn("SPECIFICITY: <complete — why nothing further applies", self.skill)

    def test_the_template_no_longer_permits_a_bare_complete(self):
        self.assertNotIn("SPECIFICITY: <complete | needs:", self.skill)

    def test_the_skill_says_a_reason_can_discharge_the_unspecified_shape(self):
        self.assertIn("A substantive reason discharges C5", self.skill)

    def test_the_skill_states_the_bare_needs_limb(self):
        """C5 fails a bare ``needs:``, so the skill has to say so too."""
        self.assertIn("a bare `complete` and a bare `needs:` both fail", self.skill)

    def test_the_skill_names_this_scanner(self):
        self.assertIn("tools/specificity_scan.py", self.skill)

    def test_the_skill_requires_a_fresh_reader_who_cannot_see_the_worksheet(self):
        self.assertIn("fresh reader", self.skill)
        self.assertIn("must not see the worksheet", self.skill)

    def test_the_skill_documents_both_second_read_commands(self):
        self.assertIn("--brief", self.skill)
        self.assertIn("--second-read", self.skill)

    def test_the_skill_documents_every_second_read_field(self):
        for field_name in scan.SECOND_READ_CODE_FIELDS + ("read_on",):
            self.assertIn(f'"{field_name}"', self.skill, field_name)

    def test_the_skill_calls_agreement_a_smoke_test_and_not_proof(self):
        lowered = self.skill.lower()
        self.assertIn("smoke test", lowered)
        self.assertIn("never proof", lowered)

    def test_the_skill_says_which_half_remains_a_reading(self):
        self.assertIn("`about` is never machine-graded", self.skill)

    def test_the_documented_record_is_valid_against_the_shipped_release(self):
        match = re.search(r"```json\n(.*?)\n```", self.skill, re.DOTALL)
        self.assertIsNotNone(match)
        documented = json.loads(match.group(1))
        documented["read_on"] = "2026-08-20"
        loaded = scan.load_second_read_record(documented, Path("documented.json"))
        self.assertTrue(loaded.ok, loaded.why_not)
        flags = [
            scan.read_flags(
                entry(
                    "I10",
                    "Essential (primary) hypertension",
                    "complete — a reason the reader did not see",
                )
            )
        ]
        connection = open_database()
        try:
            result = scan.gate_second_read(flags, loaded, connection)
        finally:
            connection.close()
        self.assertEqual(result.refusals, ())


if __name__ == "__main__":
    unittest.main()
