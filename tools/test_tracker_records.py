"""The three tracker input adapters preserve semantic record axes."""

import unittest

from tracker_records import (
    from_actions_event,
    from_command,
    records_from_actions_event,
)


def issue_event(*, action="opened", changes=None):
    event = {
        "action": action,
        "issue": {
            "number": 1152,
            "title": "Title text",
            "body": "Body text",
            "html_url": "https://example.test/issues/1152",
            "labels": [],
        },
    }
    if changes is not None:
        event["changes"] = changes
    return event


class ActionsAdapterTests(unittest.TestCase):
    def test_opened_issue_adapts_body_and_title(self):
        records = records_from_actions_event(issue_event(), "issues")

        self.assertEqual([record.surface for record in records], ["body", "title"])
        self.assertEqual([record.body for record in records], ["Body text", "Title text"])

    def test_edited_issue_adapts_only_changed_fields(self):
        records = records_from_actions_event(
            issue_event(action="edited", changes={"title": {"from": "Old"}}),
            "issues",
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].surface, "title")
        self.assertEqual(records[0].body, "Title text")

    def test_single_record_adapter_remains_body_scoped(self):
        record = from_actions_event(issue_event(), "issues")

        self.assertIsNotNone(record)
        self.assertEqual(record.surface, "body")


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
