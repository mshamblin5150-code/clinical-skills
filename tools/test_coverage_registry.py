"""Behavior of the owning coverage reader and pure topic rewrite."""
from pathlib import Path
import unittest

import coverage_registry as coverage


REGISTRY = """<!-- schema: threshold-coverage/3 -->
| topic | subject | state | artifact | record |
| --- | --- | --- | --- | --- |
| lipids | lipids | sheet | lipids.md | prior |
"""


class CoverageRegistry(unittest.TestCase):
    def test_rewrite_changes_only_the_owned_topic_line(self):
        stray = "| lipids | stray | sheet | other.md | stray |\n"
        text = stray + "\n" + REGISTRY + "\n## Other\n" + stray
        rewritten = coverage.mark_topic_unread(text, "LIPIDS", "replacement")
        self.assertEqual(rewritten, text.replace(
            "| lipids | lipids | sheet | lipids.md | prior |",
            "| lipids | lipids | unread | lipids.md | replacement |",
        ))
        entries, problems = coverage.parse_registry(text)
        self.assertEqual(problems, [])
        self.assertEqual([(e.topic, e.artifact) for e in entries], [("lipids", "lipids.md")])

    def test_rewrite_refuses_missing_or_duplicate_topic(self):
        with self.assertRaisesRegex(ValueError, "no topic"):
            coverage.mark_topic_unread(REGISTRY, "absent", "record")
        with self.assertRaisesRegex(ValueError, "duplicate topic"):
            coverage.mark_topic_unread(REGISTRY + "| lipids | ? | unread | | other |\n", "lipids", "record")

    def test_committed_registry_round_trips_without_changing_other_rows(self):
        path = Path(__file__).resolve().parent.parent / "reference/thresholds/coverage.md"
        text = path.read_text(encoding="utf-8")
        entries, problems = coverage.parse_registry(text)
        self.assertEqual(problems, [])
        self.assertTrue(entries)
        target = entries[0]
        result = coverage.mark_topic_unread(text, target.topic, "replacement")
        changed = [(a, b) for a, b in zip(text.splitlines(), result.splitlines()) if a != b]
        self.assertEqual(len(changed), 1)
        self.assertEqual(coverage.topic_entry(result, target.topic).record, "replacement")
