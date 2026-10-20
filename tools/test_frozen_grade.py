"""Synthetic public freeze/adoption contracts for ADR 0346. No patient data."""
import artifact_lock_test_support
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import frozen_grade
import file_digest
import run_status_stop_hook as hook
from test_run_status_stop_hook import command_record
from prose_bind import bind, NAMING


class FrozenFixture(unittest.TestCase):
    def reading(self, posted):
        return (f"## REREAD: post\nPOSTED: {posted}\n"
                "POST-URL: https://example.invalid/post\nREAD: retained\n"
                f"SUBMISSION-SHA256: {file_digest.sha256(self.source)}\n"
                "VERDICT: matches - synthetic retained reading\n")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.run = Path(temporary.name) / "scratch" / "runs" / "synthetic-discussion"
        self.run.mkdir(parents=True)
        self.source = self.run / "post.md"
        self.source.write_text("Synthetic approved prose.", encoding="utf-8")
        self.item = dict(skill="discussion-post", submission="post", sha256=file_digest.sha256(self.source),
                         sources=[str(self.source)], grader_args=[str(self.run)],
                         posting_route="agent", pregrade_status="clean", approval_revision=1,
                         recorded_at=1791800000)
        self.save()

    def save(self):
        (self.run / "posting-approvals.json").write_text(json.dumps(dict(
            version=1, approval_revision=self.item["approval_revision"], items=[self.item])), encoding="utf-8")


class FrozenGrade(FrozenFixture):
    def test_adoption_boundary_is_named_without_copying_it(self):
        path = Path(frozen_grade.__file__).resolve().parent.parent / "CLAUDE.md"
        self.assertEqual((), bind(frozen_grade.DECLARED_LIMITS, path.read_text(encoding="utf-8"), mode=NAMING))

    def test_frozen_grade_survives_source_edit_but_not_new_approval(self):
        frozen_grade.freeze(self.run, "discussion-post", self.item)
        first = frozen_grade.report(self.run, "post")
        self.assertIn("post: frozen", first)
        self.assertNotIn("changed", first)
        self.source.write_text("Edited source", encoding="utf-8")
        self.assertIn("source changed", frozen_grade.report(self.run, "post"))
        self.assertTrue(hook.completion_is_clean(self.run, hook.RUN_KIND_BY_SKILL["discussion-post"], self.item))
        self.item["approval_revision"] = 2
        self.save()
        self.assertIsNone(frozen_grade.report(self.run, "post"))

    def test_adoption_requires_posting_readback_and_review(self):
        (self.run / "reread.md").write_text(self.reading("2026-10-01T12:00:00Z"), encoding="utf-8")
        self.assertEqual(0, frozen_grade.adopt(self.run).adopted)
        review = self.run / "aar" / "post.md"
        review.parent.mkdir(parents=True)
        review.write_text("Retained synthetic review", encoding="utf-8")
        (self.run / frozen_grade.RECORD).unlink()
        result = frozen_grade.adopt(self.run)
        self.assertEqual(1, result.adopted)
        self.assertIn("never graded clean", frozen_grade.report(self.run, "post"))
        self.assertEqual(0, frozen_grade.adopt(self.run).adopted)

    def test_a_prebuild_approval_posted_after_landing_is_not_adopted(self):
        from datetime import datetime, timezone, timedelta
        future = datetime.fromtimestamp(frozen_grade.landing_time(), timezone.utc) + timedelta(hours=1)
        (self.run / "reread.md").write_text(self.reading(future.isoformat()), encoding="utf-8")
        review = self.run / "aar" / "post.md"
        review.parent.mkdir(parents=True)
        review.write_text("Retained review", encoding="utf-8")
        self.assertEqual(0, frozen_grade.adopt(self.run).adopted)
        self.assertIsNone(frozen_grade.report(self.run, "post"))

    def test_a_legacy_item_is_dated_by_its_posting_not_the_shared_record_mtime(self):
        self.item.pop("recorded_at")
        self.save()
        (self.run / "reread.md").write_text(self.reading("2026-10-01T12:00:00Z"), encoding="utf-8")
        review = self.run / "aar" / "post.md"
        review.parent.mkdir(parents=True)
        review.write_text("Retained synthetic review", encoding="utf-8")
        self.assertEqual(1, frozen_grade.adopt(self.run).adopted)

    def test_stored_complete_adopts_only_covered_revisions(self):
        (self.run / hook.STATE_RECORD).write_text(json.dumps(dict(status="complete",
            approval_revision=json.dumps([["discussion-post", "post", 1]], separators=(",", ":")))), encoding="utf-8")
        result = frozen_grade.adopt(self.run)
        self.assertEqual(1, result.clean)
        self.assertNotIn("never graded clean", frozen_grade.report(self.run, "post"))

    def test_reply_sitting_counts_frozen_initial_post_in_one_line(self):
        import discussion_post_scan
        frozen_grade.freeze(self.run, "discussion-post", self.item)
        reply_source = self.run / "response-synthetic.md"
        reply_source.write_text("Synthetic reply", encoding="utf-8")
        reply = {**self.item, "skill": "discussion-reply", "submission": reply_source.name,
                 "sources": [str(reply_source)], "sha256": file_digest.sha256(reply_source), "approval_revision": 2}
        (self.run / "posting-approvals.json").write_text(json.dumps(dict(version=1, approval_revision=2,
            items=[self.item, reply])), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = discussion_post_scan.main([str(self.run), "--draft", str(self.source), "--submission", "post"])
        self.assertEqual(0, status)
        self.assertEqual(1, len(output.getvalue().splitlines()))
        frozen_grade.freeze(self.run, "discussion-reply", reply)
        transcript = self.run.parent / "session.jsonl"
        transcript.write_text(json.dumps(command_record(self.run)), encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            result = hook.handle(dict(transcript_path=str(transcript),
                last_assistant_message=f"Run status: {self.run.name} — complete"))
        self.assertEqual({}, result)
        self.assertEqual("complete", json.loads((self.run / hook.STATE_RECORD).read_text())["status"])


if __name__ == "__main__":
    unittest.main()
