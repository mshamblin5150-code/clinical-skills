"""Exercise #1495 through approval's actual paired grader subprocesses.

phi-scan: synthetic
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import approval_record
import research_ledger
from test_discussion_reply_scan import BODY, REREAD, Run
from test_peer_critique_scan import REREAD as CRITIQUE_REREAD, build_run


class PrepostingApproval(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Only transcript recognition is synthetic. The paired preflight, grader
        # subprocess, durable records, and posting transition remain real.
        remarks_check = mock.patch.object(approval_record.reader_remarks, "verify", return_value=[])
        remarks_check.start()
        self.addCleanup(remarks_check.stop)
        for name in ("verify_clinician_reply", "verify_shown_text"):
            patch = mock.patch.object(
                approval_record, name,
                return_value=approval_record.ReplyVerification("verified", "synthetic transcript", 1.0),
            )
            patch.start()
            self.addCleanup(patch.stop)

    def approve(self, run, skill, artifact):
        return approval_record.approve(
            run, skill=skill, submission=artifact.name, sources=(artifact,),
            grader_args=(str(run),), content_approved=True,
            clinician_reply="Approve this entire synthetic artifact.",
        )

    def reply(self):
        run = self.root / "reply"
        run.mkdir()
        fixture = Run(run, posted=False)
        (run / "reread.md").unlink()
        return fixture

    def test_a_clean_unposted_reply_records_a_clean_approval(self):
        run = self.reply().root
        self.approve(run, "discussion-reply", run / "response-maren.md")
        item = json.loads((run / approval_record.RECORD).read_text(encoding="utf-8"))["items"][0]
        self.assertEqual("clean", item["pregrade_status"])
        self.assertEqual("awaiting-posting", approval_record.posting_route(
            run, skill="discussion-reply", submission="response-maren.md"))

    def test_a_clean_unposted_critique_records_a_clean_approval(self):
        run = build_run(root=self.root / "critique", reread=None, posted=False)
        self.approve(run, "peer-critique", run / "critique.md")
        item = json.loads((run / approval_record.RECORD).read_text(encoding="utf-8"))["items"][0]
        self.assertEqual("clean", item["pregrade_status"])
        self.assertEqual("awaiting-posting", approval_record.posting_route(
            run, skill="peer-critique", submission="critique.md"))

    def test_posted_reply_one_without_a_reading_refuses_reply_twos_approval(self):
        fixture = self.reply()
        run = fixture.root
        first = run / "response-maren.md"
        self.approve(run, "discussion-reply", first)
        approval_record.record_agent_posting(run, skill="discussion-reply", submission=first.name)
        second = run / "response-noah.md"
        second.write_text(BODY.replace("Maren,", "Noah,").replace("Quill", "Rowan"), encoding="utf-8")
        (run / "posts" / "noah.md").write_text("AUTHOR: Noah Reed\n", encoding="utf-8")
        claims = run / "claims.md"
        first_claims = claims.read_text(encoding="utf-8")
        second_claims = first_claims.replace("[REPLY: maren]", "[REPLY: noah]").replace("Quill", "Rowan")
        heading = research_ledger.read_records(second_claims)[0].claim
        second_claims = second_claims.replace(
            research_ledger.heading_digest(research_ledger.read_records(first_claims)[0].claim),
            research_ledger.heading_digest(heading),
        )
        claims.write_text(first_claims + "\n" + second_claims, encoding="utf-8")
        fixture.write_heading_read()
        with self.assertRaisesRegex(approval_record.ApprovalRecordError, "missing-posted-reading"):
            self.approve(run, "discussion-reply", second)
        items = json.loads((run / approval_record.RECORD).read_text(encoding="utf-8"))["items"]
        self.assertEqual([first.name], [item["submission"] for item in items])
        (run / "reread.md").write_text(
            REREAD.format(submission_sha256=approval_record.source_sha256((first,))),
            encoding="utf-8",
        )
        self.approve(run, "discussion-reply", second)
        items = json.loads((run / approval_record.RECORD).read_text(encoding="utf-8"))["items"]
        self.assertEqual([first.name, second.name], [item["submission"] for item in items])

    def test_reapproval_resets_a_recorded_posting_to_awaiting(self):
        run = build_run(root=self.root / "critique", reread=None, posted=False)
        artifact = run / "critique.md"
        approval = self.approve(run, "peer-critique", artifact)
        approval_record.record_clinician_posting(run, skill="peer-critique", submission=artifact.name)
        (run / "reread.md").write_text(
            CRITIQUE_REREAD.format(submission_sha256=approval.sha256),
            encoding="utf-8",
        )
        self.approve(run, "peer-critique", artifact)
        self.assertEqual("awaiting-posting", approval_record.posting_route(
            run, skill="peer-critique", submission=artifact.name))
        (run / "reread.md").unlink()
        status, report = approval_record._pre_post_grade("peer-critique", (str(run),))
        self.assertEqual(0, status, report)

    def test_terminal_completion_still_refuses_an_approved_unposted_item(self):
        fixture = self.reply()
        run = fixture.root
        artifact = run / "response-maren.md"
        self.approve(run, "discussion-reply", artifact)
        failed, report = approval_record.completion_gate(run, "discussion-reply", artifact.name)
        self.assertTrue(failed, report)


if __name__ == "__main__":
    unittest.main()
