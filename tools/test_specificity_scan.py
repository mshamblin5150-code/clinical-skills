"""Cover ``specificity_scan``'s parser against synthetic worksheets.

Every worksheet here is written in this file. There is no committed run of
``icd10-cpt`` to test against -- a run directory is a patient record under
``scratch/`` -- so the fixtures are invented, the way ``test_skills_mirror``
builds throwaway checkouts rather than touching the real one.

``TheSkillSaysWhatThisChecks`` is the one test that reads a committed file, and
it is there for ``test_spelling_scan``'s reason: a scanner that drifts from the
file a reader opens is worse than no scanner, because it reads as agreement.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

import specificity_scan as scan
from icd10_lookup import normalize, open_database

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


class TheParserPairsAFlagWithItsDescriptor(unittest.TestCase):
    def test_it_reads_the_code_and_descriptor_above_the_flag(self):
        flags = scan.read_flags(entry("R12", "Heartburn", "complete — R12 has no further axis"))
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0].code, "R12")
        self.assertEqual(flags[0].descriptor, "Heartburn")
        self.assertEqual(flags[0].keyword, "complete")

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
    """The first of C5's two tests, and it reaches both branches."""

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


class AnUnspecifiedDescriptorMayNotReadComplete(unittest.TestCase):
    """C5's second test. The descriptor is C2's verbatim official string."""

    def test_unspecified_in_the_descriptor_fails_a_complete(self):
        text = entry("M19.90", "Unspecified osteoarthritis, unspecified site", "complete — no further axis")
        self.assertEqual([f.kind for f in scan.findings(scan.read_flags(text))], ["unspecified-complete"])

    def test_the_same_descriptor_passes_with_needs(self):
        text = entry("M19.90", "Unspecified osteoarthritis, unspecified site", "needs: site")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_not_specified_fires_too(self):
        text = entry("N39.0", "Urinary tract infection, site not specified", "complete — no axis remains")
        self.assertEqual([f.kind for f in scan.findings(scan.read_flags(text))], ["unspecified-complete"])

    def test_an_other_residual_is_not_an_unspecified_one(self):
        """``R06.89`` says the finding fits no named code, not that the note is thin."""
        text = entry("R06.89", "Other abnormalities of breathing", "complete — R06.89 is the residual")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_other_specified_is_not_not_specified(self):
        text = entry("R79.89", "Other specified abnormal findings of blood chemistry", "complete — residual")
        self.assertEqual(scan.findings(scan.read_flags(text)), [])

    def test_a_bare_complete_on_an_unspecified_descriptor_fails_both_ways(self):
        flags = scan.read_flags(entry("J02.9", "Acute pharyngitis, unspecified", "complete"))
        self.assertEqual(
            sorted(f.kind for f in scan.findings(flags)),
            ["bare-flag", "unspecified-complete"],
        )


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

    def test_one_flag_failing_both_tests_counts_as_one_flag(self):
        """The two counters sum to 2 and exactly one line is at fault."""
        self.assertEqual(self.survey.bare_flags + self.survey.unspecified_complete, 2)
        self.assertEqual(self.survey.failing_flags, 1)
        self.assertEqual(len(self.survey.findings), 2)

    def test_no_descriptor_reaches_the_default_report(self):
        report = scan.format_report(self.survey, source="a-run", show=False)
        self.assertNotIn("osteoarthritis", report)
        self.assertNotIn("hypertension", report)
        self.assertNotIn("M19.90", report)

    def test_show_names_the_code_and_the_flag(self):
        report = scan.format_report(self.survey, source="a-run", show=True)
        self.assertIn("M19.90", report)
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

    def test_the_skill_states_the_unspecified_rule(self):
        self.assertIn("does not read `complete` at all", self.skill)

    def test_the_skill_states_the_bare_needs_limb(self):
        """C5 fails a bare ``needs:``, so the skill has to say so too."""
        self.assertIn("a bare `complete` and a bare `needs:` both fail", self.skill)

    def test_the_skill_names_this_scanner(self):
        self.assertIn("tools/specificity_scan.py", self.skill)


if __name__ == "__main__":
    unittest.main()
