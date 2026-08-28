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


if __name__ == "__main__":
    unittest.main()
