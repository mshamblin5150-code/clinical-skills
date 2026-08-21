"""A merged PR leaves an immutable state receipt on every ticket it names."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tracker_merge_receipt as receipt


def merged_pr(body: str, **changes):
    document = {
        "number": 401,
        "url": "https://github.com/example/clinical-skills/pull/401",
        "title": "Implement the tracker receipt",
        "body": body,
        "baseRefName": "main",
        "mergedAt": "2026-08-20T22:30:00Z",
        "mergeCommit": {"oid": "0123456789abcdef0123456789abcdef01234567"},
        "commits": [],
    }
    document.update(changes)
    return document


class ExplicitTicketReferencesBecomeReceipts(unittest.TestCase):
    def test_whole_and_partial_ticket_forms_each_get_one_receipt(self):
        document = merged_pr(
            "Closes #290\n\nPart of #298\n\nImplements #300's lead 2\n"
        )

        rows = receipt.plan_receipts(document)

        self.assertEqual([row.ticket for row in rows], [290, 298, 300])
        for row in rows:
            self.assertIn("PR #401", row.body)
            self.assertIn("`main`", row.body)
            self.assertIn("`0123456789abcdef0123456789abcdef01234567`", row.body)
            self.assertIn("2026-08-20", row.body)
            self.assertIn("does not make later names or claims current", row.body)

    def test_distinct_leads_on_one_ticket_keep_their_claim_identity(self):
        document = merged_pr(
            "Implements #300's lead 1\n\nImplements #300's lead 2\n"
        )

        rows = receipt.plan_receipts(document)

        self.assertEqual([row.ticket for row in rows], [300, 300])
        self.assertIn("`Implements #300's lead 1`", rows[0].body)
        self.assertIn("`Implements #300's lead 2`", rows[1].body)

    def test_duplicate_references_across_pr_and_commit_text_are_one_receipt(self):
        document = merged_pr("Part of #290\n")
        document["commits"] = [
            {
                "messageHeadline": "Implement receipt",
                "messageBody": "Part of #290\n",
            }
        ]

        self.assertEqual(
            [row.ticket for row in receipt.plan_receipts(document)],
            [290],
        )

    def test_prose_and_ambiguous_references_do_not_bind(self):
        document = merged_pr(
            "This follows #290.\n"
            "The branch was merged with main for #278.\n"
            "Implements the idea in #300.\n"
        )

        self.assertEqual(receipt.plan_receipts(document), [])

    def test_an_unbounded_partial_description_is_not_republished(self):
        document = merged_pr("Implements #300's arbitrary claim with `markup`\n")

        self.assertEqual(receipt.plan_receipts(document), [])

    def test_a_pr_title_is_not_a_ticket_binding(self):
        document = merged_pr("", title="Part of #290")

        self.assertEqual(receipt.plan_receipts(document), [])


class OnlyACompletedMainMergeCanProduceReceipts(unittest.TestCase):
    def test_an_open_pr_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not merged"):
            receipt.plan_receipts(merged_pr("Part of #290\n", mergedAt=None))

    def test_a_merge_to_another_base_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "base branch"):
            receipt.plan_receipts(
                merged_pr("Part of #290\n", baseRefName="release")
            )

    def test_a_missing_full_merge_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "full merge commit"):
            receipt.plan_receipts(
                merged_pr("Part of #290\n", mergeCommit={"oid": "0123456"})
            )

    def test_the_pr_url_must_name_the_same_pull_request(self):
        with self.assertRaisesRegex(ValueError, "pull request URL"):
            receipt.plan_receipts(
                merged_pr(
                    "Part of #290\n",
                    url="https://github.com/example/clinical-skills/pull/999",
                )
            )


class CommandLineOutputIsMachineReadable(unittest.TestCase):
    def test_json_lines_mode_reads_standard_input(self):
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(io.StringIO()),
            mock.patch("sys.stdin", io.StringIO(json.dumps(merged_pr("Part of #290\n")))),
        ):
            status = receipt.main(["-"])

        self.assertEqual(status, 0)
        record = json.loads(output.getvalue())
        self.assertEqual(record["ticket"], 290)
        self.assertIn("PR #401", record["body"])

    def test_malformed_input_is_not_a_clean_empty_plan(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "bad.json"
            path.write_text("[]", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                status = receipt.main([str(path)])

        self.assertEqual(status, 2)

if __name__ == "__main__":
    unittest.main()
