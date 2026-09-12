"""Public parser tests for shared discussion artifact shapes.

All records are synthetic. No classmate or patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import discussion_artifact as artifact
from prose_bind import NAMING, bind
from run_grader import EvidenceDisposition


APA_SHEET = Path(__file__).resolve().parents[1] / "skills" / "_shared" / "reference" / "apa7.md"


def republished_work_rows() -> tuple[tuple[str, str], ...]:
    sheet = APA_SHEET.read_text(encoding="utf-8")
    section = sheet.split(
        "## 31. Two dates for republished, translated, reissued, religious, and classical works",
        1,
    )[1].split("\n## ", 1)[0]
    return tuple(
        (cells[0], cells[1])
        for line in section.splitlines()
        for cells in (re.findall(r"`([^`]*)`", line),)
        if line.startswith("| `") and len(cells) >= 2
    )


class ReferenceKeysUseTheTitleProper(unittest.TestCase):
    def test_a_trailing_translator_credit_is_not_part_of_the_key(self):
        entry = next(
            entry
            for entry, _citation in republished_work_rows()
            if entry.startswith("The epic of Gilgamesh")
        )

        self.assertEqual(
            (("epicofgilgamesh", "1998"),),
            artifact.reference_keys(entry),
        )


class CitationResolutionIsDirectional(unittest.TestCase):
    def test_a_shortened_title_resolves_without_becoming_a_member(self):
        references = artifact.ReferenceKeySet.from_references(
            (
                "Diagnostic and statistical manual of mental disorders "
                "(5th ed., text rev.). (2022). Publisher.",
            )
        )
        citation_key = ("diagnosticandstatisticalmanual", "2022")

        self.assertTrue(references.resolves(citation_key))
        self.assertNotIn(citation_key, references)
        self.assertNotIn(citation_key, tuple(references))

    def test_a_personal_surname_still_requires_equality(self):
        references = artifact.ReferenceKeySet.from_references(
            ("Smith, J. (2022). A title. Publisher.",)
        )

        self.assertFalse(references.resolves(("smi", "2022")))
        self.assertTrue(references.resolves(("smith", "2022")))

    def test_every_republished_work_form_in_the_apa_sheet_resolves(self):
        rows = republished_work_rows()
        self.assertTrue(rows)

        for entry, written_citation in rows:
            with self.subTest(citation=written_citation):
                references = artifact.ReferenceKeySet.from_references((entry,))
                citations = artifact.read_citations(written_citation, references)
                occurrences = artifact.citation_occurrence_keys(citations)

                self.assertTrue(citations)
                self.assertTrue(
                    all(
                        any(references.resolves(key) for key in occurrence)
                        for occurrence in occurrences
                    )
                )

    def test_synthetic_credit_edition_and_shortened_title_forms_resolve(self):
        cases = (
            (
                "The handbook of nursing (J. Smith, Ed.). (2021). Publisher.",
                ("handbookofnursing", "2021"),
            ),
            (
                "Nursing today (2nd ed.). (2020). Publisher.",
                ("nursingtoday", "2020"),
            ),
            (
                "Diagnostic and statistical manual of mental disorders "
                "(5th ed., text rev.). (2022). Publisher.",
                ("diagnosticandstatisticalmanual", "2022"),
            ),
        )

        for entry, citation_key in cases:
            with self.subTest(entry=entry):
                references = artifact.ReferenceKeySet.from_references((entry,))
                self.assertTrue(references.resolves(citation_key))

    def test_legal_entries_are_classified_before_the_no_surname_fallback(self):
        cases = (
            (
                "Professional and Vocational Regulations, 16 CCR § 1481",
                (("professionalandvocationalregulations", ""),),
            ),
            (
                "Eligibility for prescriptive authority, W. Va. Code § 30-7-15b",
                (("eligibilityforprescriptiveauthority", ""),),
            ),
            (
                "Consolidated Appropriations Act, 2023, Pub. L. No. 117-328, § 1263",
                (("consolidatedappropriationsact2023", ""),),
            ),
            (
                "Payment for nurse practitioners' services, 42 C.F.R. § 414.56",
                (("paymentfornursepractitionersservices", ""),),
            ),
            (
                "Advanced practice registered nurse licensure requirements "
                "(W. Va. Code R. § 19-7, 2024)",
                (("advancedpracticeregisterednurselicensurerequirements", ""),),
            ),
            ("King James Bible.", ()),
            ("World Health Organization.", ()),
            ("Smith, J.", ()),
        )

        for entry, expected in cases:
            with self.subTest(entry=entry):
                self.assertEqual(expected, artifact.reference_keys(entry))

    def test_the_three_resolution_residues_share_one_declared_object(self):
        self.assertEqual(3, len(artifact.CITATION_RESOLUTION_NOT_REACHED))
        self.assertTrue(
            all(
                disposition is EvidenceDisposition.BEHAVIOR
                for _subject, _reason, disposition in artifact.CITATION_RESOLUTION_NOT_REACHED
            )
        )
        self.assertEqual(
            (),
            bind(
                artifact.CITATION_RESOLUTION_NOT_REACHED,
                artifact.__doc__ or "",
                mode=NAMING,
            ),
        )


class PostedReadingsAreSharedArtifacts(unittest.TestCase):
    def test_one_record_preserves_the_entry_and_verdict_substance(self):
        records = artifact.read_posted_readings(
            """\
## REREAD: response-maren.md
POST-URL: https://example.org/courses/1/discussion_topics/2?entry_id=31
POSTED: 2026-08-28T20:10:00-04:00
READ: 2026-08-28
VERDICT: matches - The paragraphs, references, and bold label are present.
"""
        )

        self.assertEqual(1, len(records))
        self.assertEqual("response-maren.md", records[0].artifact)
        self.assertEqual("matches", records[0].verdict)
        self.assertEqual(
            "The paragraphs, references, and bold label are present.",
            records[0].verdict_detail,
        )
        self.assertEqual((), records[0].missing_fields)

    def test_an_absent_file_can_be_represented_by_no_records(self):
        self.assertEqual((), artifact.read_posted_readings(""))

    def test_duplicate_entry_records_are_unreadable(self):
        record = """\
## REREAD: response-maren.md
POST-URL: https://example.org/topic?entry_id=31
POSTED: 2026-08-28T20:10:00-04:00
READ: 2026-08-28
VERDICT: matches - The entry was read from the board.
"""

        with self.assertRaisesRegex(ValueError, "duplicate REREAD"):
            artifact.read_posted_readings(record + "\n" + record)

    def test_nonrecord_content_is_unreadable(self):
        with self.assertRaisesRegex(ValueError, "no readable REREAD"):
            artifact.read_posted_readings("VERDICT: matches - trust me\n")

    def test_unrecognized_content_inside_a_record_is_unreadable(self):
        with self.assertRaisesRegex(ValueError, "unreadable content"):
            artifact.read_posted_readings(
                """\
## REREAD: post.md
POST-URL: https://example.org/topic?entry_id=41
POSTED: 2026-08-28T19:30:00-04:00
READ: 2026-08-28
VERDICT: matches - The board was read.
TRUST-ME: yes
"""
            )

    def test_both_discussion_skills_publish_a_record_the_shared_parser_reads(self):
        root = Path(__file__).resolve().parents[1]
        for skill_name in ("discussion-post", "discussion-reply"):
            with self.subTest(skill=skill_name):
                skill = (root / "skills" / skill_name / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                block = re.search(
                    r"```text\n(?P<record>## REREAD:.*?VERDICT:.*?\n)```",
                    skill,
                    re.DOTALL,
                )
                self.assertIsNotNone(block)
                records = artifact.read_posted_readings(block.group("record"))
                self.assertEqual(1, len(records))
                self.assertEqual((), records[0].missing_fields)


if __name__ == "__main__":
    unittest.main()
