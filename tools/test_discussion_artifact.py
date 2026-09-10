"""Public parser tests for shared discussion artifact shapes.

All records are synthetic. No classmate or patient is represented here.

phi-scan: synthetic
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import discussion_artifact as artifact


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


class DatedReferenceEntriesAreReferences(unittest.TestCase):
    """apa7.md rules a ``(Year, Month Day)`` date element for several forms.

    The population is taken from the sheet's abstracted entry forms, which is a
    different text from the synthesized examples the extraction reads, so a
    dated example the extraction fails to see makes the two counts disagree.
    """

    DATED_ELEMENT = re.compile(r"\((?P<year>(?:19|20)\d{2}), [A-Z][a-z]+ \d{1,2}\)")

    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        sheet = (root / "skills" / "_shared" / "reference" / "apa7.md").read_text(
            encoding="utf-8"
        )
        blocks = [" ".join(block.split()) for block in re.split(r"\n\s*\n", sheet)]
        cls.dated_forms = [
            block
            for block in blocks
            if block.startswith("**Abstracted entry form:**")
            and "(Year, Month Day" in block
        ]
        cls.dated_examples = [
            block.removeprefix("**Synthesized example:**").strip()
            for block in blocks
            if block.startswith("**Synthesized example:**")
            and cls.DATED_ELEMENT.search(block)
        ]

    def test_every_dated_form_in_the_sheet_has_its_example_read(self):
        self.assertTrue(self.dated_forms, "apa7.md no longer publishes a dated form")
        self.assertEqual(len(self.dated_forms), len(self.dated_examples))

    def test_every_dated_example_yields_its_author_and_year(self):
        for entry in self.dated_examples:
            with self.subTest(entry=entry[:60]):
                year = self.DATED_ELEMENT.search(entry).group("year")
                keys = artifact.reference_keys(entry)
                self.assertTrue(keys)
                self.assertEqual({year}, {key_year for _key, key_year in keys})

    def test_the_date_element_captures_only_the_year(self):
        match = artifact.REFERENCE_YEAR.search(
            "Office of Family Health. (2026, June 9). *Preparing for a visit*."
        )
        self.assertIsNotNone(match)
        self.assertEqual("2026", match.group("year"))

    def test_a_year_only_entry_still_reads(self):
        self.assertEqual(
            (("officeofneighborhoodhealth", "2025"),),
            artifact.reference_keys(
                "Office of Neighborhood Health. (2025). *Preventing heat illness*."
            ),
        )


if __name__ == "__main__":
    unittest.main()
