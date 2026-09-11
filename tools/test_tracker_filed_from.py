"""Tests for the Filed-from GitHub-event and open-ticket grader."""

from __future__ import annotations

from datetime import timedelta
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import tracker_filed_from as filed_from


REPO_ROOT = Path(__file__).resolve().parent.parent
ISSUE_TRACKER = REPO_ROOT / "docs" / "agents" / "issue-tracker.md"
AAR_SKILL = REPO_ROOT / "skills" / "aar" / "SKILL.md"
MAP_COMMIT = "a" * 40
MAP_PRODUCER = "b" * 64


def map_body() -> str:
    return (
        "<!-- implementation-map:v1:state:end -->\n\n"
        "## Snapshot\n"
        f"- producer: `tools/implementation_map.py sha256:{MAP_PRODUCER}`\n"
        f"- default-branch commit: `{MAP_COMMIT}`\n"
    )


def opened_event(body: str, *, created_at: str) -> dict:
    return {
        "action": "opened",
        "issue": {
            "number": 17,
            "body": body,
            "created_at": created_at,
            "html_url": "https://example.invalid/issues/17",
        },
    }


class GithubIssueEventsAreReported(unittest.TestCase):
    def test_an_opened_issue_at_the_cutoff_without_the_line_is_reported(self) -> None:
        event = opened_event(
            "Body without its filing record.",
            created_at=filed_from.FILED_FROM_CUTOFF.isoformat().replace("+00:00", "Z"),
        )

        scan = filed_from.grade_event(event, "issues")

        self.assertEqual([row.rule for row in scan.findings], ["filed-from:opened"])
        self.assertIn("https://example.invalid/issues/17", scan.report)
        self.assertNotIn("Body without", scan.report)

    def test_an_edited_issue_that_drops_the_previous_line_is_reported(self) -> None:
        previous = "**Filed from:** the architecture review, 2026-09-11.\n\nOld."
        event = {
            "action": "edited",
            "issue": {
                "number": 17,
                "body": "Replacement without its filing record.",
                "created_at": "2026-09-01T00:00:00Z",
                "html_url": "https://example.invalid/issues/17",
            },
            "changes": {"body": {"from": previous}},
        }

        scan = filed_from.grade_event(event, "issues")

        self.assertEqual([row.rule for row in scan.findings], ["filed-from:edited"])
        self.assertNotIn(previous, scan.report)

    def test_an_opened_issue_before_the_cutoff_is_not_reported(self) -> None:
        before = filed_from.FILED_FROM_CUTOFF - timedelta(seconds=1)
        event = opened_event(
            "Body without its filing record.",
            created_at=before.isoformat().replace("+00:00", "Z"),
        )

        scan = filed_from.grade_event(event, "issues")

        self.assertEqual(scan.findings, ())

    def test_an_edited_issue_that_alters_the_previous_line_is_reported(self) -> None:
        previous = "**Filed from:** the architecture review, 2026-09-11.\n\nOld."
        event = {
            "action": "edited",
            "issue": {
                "number": 17,
                "body": "**Filed from:** a later rewrite, 2026-09-12.\n\nNew.",
                "created_at": "2026-09-01T00:00:00Z",
                "html_url": "https://example.invalid/issues/17",
            },
            "changes": {"body": {"from": previous}},
        }

        scan = filed_from.grade_event(event, "issues")

        self.assertEqual([row.rule for row in scan.findings], ["filed-from:edited"])

    def test_an_edit_that_keeps_the_line_identical_is_not_reported(self) -> None:
        line = "**Filed from:** the architecture review, 2026-09-11."
        event = {
            "action": "edited",
            "issue": {
                "number": 17,
                "body": line + "\n*Corrected 2026-09-12: source clarified.*\n\nNew.",
                "created_at": "2026-09-01T00:00:00Z",
                "html_url": "https://example.invalid/issues/17",
            },
            "changes": {"body": {"from": line + "\n\nOld."}},
        }

        scan = filed_from.grade_event(event, "issues")

        self.assertEqual(scan.findings, ())

    def test_a_map_stamped_body_is_not_reported(self) -> None:
        event = opened_event(
            map_body(),
            created_at=filed_from.FILED_FROM_CUTOFF.isoformat().replace("+00:00", "Z"),
        )

        with mock.patch(
            "implementation_map.producer_identity", return_value=MAP_PRODUCER
        ):
            scan = filed_from.grade_event(event, "issues")

        self.assertEqual(scan.findings, ())
        self.assertIn("implementation map not graded", scan.report)

    def test_a_producer_looking_bullet_alone_does_not_exempt_a_body(self) -> None:
        body = (
            f"- producer: `tools/implementation_map.py sha256:{MAP_PRODUCER}`"
        )
        event = opened_event(
            body,
            created_at=filed_from.FILED_FROM_CUTOFF.isoformat().replace("+00:00", "Z"),
        )

        scan = filed_from.grade_event(event, "issues")

        self.assertEqual([row.rule for row in scan.findings], ["filed-from:opened"])


class TheFixedPositionFollowsRecordScope(unittest.TestCase):
    def test_each_record_scope_places_the_line_immediately_beneath_it(self) -> None:
        scopes = (
            (
                "> **Branch state:** `codex/ticket-17` at `"
                + "a" * 40
                + "` is not on `main` as of `2026-09-11`.\n"
            ),
            (
                "> **Branch state:** this text rests on `main` at `"
                + "a" * 40
                + "` as of `2026-09-11`.\n"
            ),
            (
                "> **Cited record state:** `docs/adr/9999-unmerged.md` is not "
                "on `main` as of `2026-09-11`.\n"
            ),
        )
        line = "**Filed from:** the architecture review, 2026-09-11."

        for scope in scopes:
            with self.subTest(scope=scope.partition(":**")[0]):
                self.assertEqual(filed_from.fixed_position_line(scope + line), line)
                self.assertIsNone(
                    filed_from.fixed_position_line(scope + "\n" + line)
                )

    def test_correction_placement_is_explicitly_outside_the_fixed_line_grade(self) -> None:
        line = "**Filed from:** the architecture review, 2026-09-11."
        grade = filed_from.grade_publication(
            line + "\n\n*Correction with no date.*",
            ("issue", "edit"),
            current_body=line + "\n\nOld.",
        )

        self.assertIsNone(grade.rule)
        self.assertIn("correction form and placement NOT GRADED", grade.report)


class TheCommandGradesOneGithubEvent(unittest.TestCase):
    def test_a_reported_event_exits_one_without_printing_the_body(self) -> None:
        event = opened_event(
            "Body without its filing record.",
            created_at=filed_from.FILED_FROM_CUTOFF.isoformat().replace("+00:00", "Z"),
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "event.json"
            path.write_text(json.dumps(event), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = filed_from.main(
                    ["--github-event", str(path), "--event-name", "issues"]
                )

        self.assertEqual(status, 1)
        self.assertIn("filed-from:opened", stdout.getvalue())
        self.assertNotIn("Body without", stdout.getvalue())


class TheOpenTicketSweepListsMissingLines(unittest.TestCase):
    def test_a_read_that_reaches_its_cap_is_not_complete(self) -> None:
        created_at = filed_from.FILED_FROM_CUTOFF.isoformat().replace("+00:00", "Z")
        rows = [
            {
                "number": 17,
                "body": "Missing.",
                "createdAt": created_at,
                "state": "OPEN",
                "url": "https://example.invalid/issues/17",
            },
            {
                "number": 18,
                "body": "**Filed from:** the review, 2026-09-11.\n\nPresent.",
                "createdAt": created_at,
                "state": "OPEN",
                "url": "https://example.invalid/issues/18",
            },
        ]

        scan = filed_from.grade_open_issues(rows, cap=2)

        self.assertFalse(scan.complete)
        self.assertEqual([row.url for row in scan.findings], [rows[0]["url"]])
        self.assertIn("NOT COMPLETE", scan.report)
        self.assertIn("records read 2", scan.report)
        self.assertIn("eligible records 2", scan.report)
        self.assertIn("unread records 0", scan.report)

    def test_an_unread_row_is_counted_and_makes_the_sweep_incomplete(self) -> None:
        scan = filed_from.grade_open_issues(
            [{"number": 17, "state": "OPEN"}], cap=1000
        )

        self.assertFalse(scan.complete)
        self.assertEqual(scan.records, 1)
        self.assertEqual(scan.eligible, 0)
        self.assertEqual(scan.unread, 1)
        self.assertIn("unread records 1", scan.report)

    def test_the_harvest_command_lists_a_missing_post_cutoff_issue(self) -> None:
        rows = [
            {
                "number": 17,
                "body": "Missing.",
                "createdAt": filed_from.FILED_FROM_CUTOFF.isoformat().replace(
                    "+00:00", "Z"
                ),
                "state": "OPEN",
                "url": "https://example.invalid/issues/17",
            }
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "open.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = filed_from.main(
                    ["--harvest", str(path), "--cap", "1000"]
                )

        self.assertEqual(status, 1)
        self.assertIn("filed-from:sweep", stdout.getvalue())
        self.assertIn("read complete", stdout.getvalue())


class TheWrittenRuleNamesItsOwnedSources(unittest.TestCase):
    def test_the_maintainer_rule_points_at_context_and_the_shared_cutoff(self) -> None:
        text = ISSUE_TRACKER.read_text(encoding="utf-8")

        self.assertIn("[`CONTEXT.md`](../../CONTEXT.md#filed-from-line)", text)
        self.assertIn("tracker_filed_from.FILED_FROM_CUTOFF", text)
        self.assertIn("tracker_filed_from.py --harvest", text)
        self.assertIn("returns exactly the cap", text)

    def test_the_aar_requires_the_exact_filed_from_form(self) -> None:
        text = AAR_SKILL.read_text(encoding="utf-8")

        self.assertIn(
            "**Filed from:** the after-action review of a <skill> run "
            "(<course> <module>), <YYYY-MM-DD>.",
            text,
        )
