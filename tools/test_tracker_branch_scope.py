"""In-flight issue text carries dated, directional branch provenance."""

import contextlib
import io
import json
import unittest
from unittest import mock

import tracker_branch_scope as scope
import tracker_merge_receipt as receipt


MARKER = (
    "> **Branch state:** `codex/ticket-290` at "
    "`abcdef0123456789abcdef0123456789abcdef01` is not on `main` as of "
    "`2026-08-20`.\n\n"
)


def comment_event(body: str, labels=("in flight",)):
    return {
        "issue": {
            "number": 290,
            "html_url": "https://github.com/example/repo/issues/290",
            "labels": [{"name": label} for label in labels],
        },
        "comment": {
            "body": body,
            "html_url": "https://github.com/example/repo/issues/290#comment-1",
        },
    }


class InFlightTrackerRecordsCarryTheirOwnBranchScope(unittest.TestCase):
    def test_an_in_flight_comment_without_the_scope_is_a_finding(self):
        result = scope.grade(
            comment_event("The new command now emits a receipt."),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)
        self.assertIn("missing Branch state", result.report)
        self.assertNotIn("The new command", result.report)

    def test_the_exact_dated_scope_is_clean(self):
        result = scope.grade(
            comment_event(MARKER + "The branch adds the command."),
            "issue_comment",
        )

        self.assertEqual(result.status, 0)

    def test_labeling_an_issue_grades_its_existing_body(self):
        event = comment_event("")
        event["issue"]["body"] = "The branch adds the command."

        result = scope.grade(event, "issues")

        self.assertEqual(result.status, 1)
        self.assertIn("issues/290", result.report)

    def test_a_record_outside_an_in_flight_issue_is_not_claimed(self):
        result = scope.grade(
            comment_event("Ordinary tracker prose.", labels=("bug",)),
            "issue_comment",
        )

        self.assertEqual(result.status, 0)

    def test_a_completion_comment_cannot_escape_through_a_missing_label(self):
        event = comment_event(
            "Ruled and built, 2026-08-20.\n\nCommit a36ffae records the ruling.",
            labels=("bug", "grilling"),
        )

        result = scope.grade(event, "issue_comment")

        self.assertEqual(result.status, 1)
        self.assertIn("self-declares completion", result.report)

    def test_an_immutable_main_receipt_satisfies_a_completion_comment(self):
        document = {
            "number": 376,
            "url": "https://github.com/example/repo/pull/376",
            "body": "Closes #290",
            "baseRefName": "main",
            "mergedAt": "2026-08-20T12:00:00Z",
            "mergeCommit": {"oid": "abcdef0123456789abcdef0123456789abcdef01"},
            "commits": [],
        }
        body = receipt.plan_receipts(document)[0].body

        result = scope.grade(
            comment_event(body, labels=("bug", "in flight")),
            "issue_comment",
        )

        self.assertEqual(result.status, 0)

    def test_a_canonical_receipt_for_another_ticket_is_not_accepted(self):
        document = {
            "number": 376,
            "url": "https://github.com/example/repo/pull/376",
            "body": "Closes #283",
            "baseRefName": "main",
            "mergedAt": "2026-08-20T12:00:00Z",
            "mergeCommit": {"oid": "abcdef0123456789abcdef0123456789abcdef01"},
            "commits": [],
        }
        body = receipt.plan_receipts(document)[0].body

        result = scope.grade(
            comment_event(body, labels=("bug", "in flight")),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)

    def test_a_truncated_receipt_prefix_is_not_accepted(self):
        body = (
            "Merged into `main` by [PR #376](https://github.com/example/repo/pull/376) "
            "at `abcdef0123456789abcdef0123456789abcdef01` on 2026-08-20."
        )

        result = scope.grade(
            comment_event(body, labels=("bug", "in flight")),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)

    def test_a_receipt_with_a_mismatched_pr_url_is_not_accepted(self):
        document = {
            "number": 376,
            "url": "https://github.com/example/repo/pull/376",
            "body": "Closes #283",
            "baseRefName": "main",
            "mergedAt": "2026-08-20T12:00:00Z",
            "mergeCommit": {"oid": "abcdef0123456789abcdef0123456789abcdef01"},
            "commits": [],
        }
        body = receipt.plan_receipts(document)[0].body.replace("pull/376", "pull/999")

        result = scope.grade(
            comment_event(body, labels=("bug", "in flight")),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)

    def test_a_pull_request_comment_is_not_an_issue_branch_claim(self):
        event = comment_event("PR discussion.")
        event["issue"]["pull_request"] = {
            "url": "https://api.github.com/repos/example/repo/pulls/401"
        }

        result = scope.grade(event, "issue_comment")

        self.assertEqual(result.status, 0)


class CommandLineStatusPreservesTheFinding(unittest.TestCase):
    def test_event_mode_returns_the_scope_finding_status(self):
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(io.StringIO()),
            mock.patch(
                "sys.stdin",
                io.StringIO(json.dumps(comment_event("The branch adds the command."))),
            ),
        ):
            status = scope.main(
                ["--github-event", "-", "--event-name", "issue_comment"]
            )

        self.assertEqual(status, 1)
        self.assertIn("missing Branch state", output.getvalue())


if __name__ == "__main__":
    unittest.main()
