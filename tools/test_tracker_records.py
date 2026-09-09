"""The three tracker input adapters preserve semantic record axes."""

import unittest

from tracker_records import from_command


class CommandAdapterTests(unittest.TestCase):
    def test_issue_title_is_not_reclassified_as_a_pull_request(self):
        record = from_command(
            "Issue title",
            url="draft title",
            number=None,
            labels=(),
            route=("issue", "create"),
            field="title",
        )

        self.assertEqual(record.container, "issue")
        self.assertEqual(record.surface, "title")


if __name__ == "__main__":
    unittest.main()
