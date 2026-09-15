"""Bind the tracker publication hosts through their public behavior. Issue #1149.

phi-scan: synthetic
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import tracker_event_checks
import tracker_publication_correspondence as correspondence
import tracker_publish_hook
import phi_scan
from prose_bind import NAMING, bind, section as markdown_section


REPO_ROOT = Path(__file__).resolve().parent.parent


def hook_payload(command: str) -> dict[str, object]:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


def issue_event(action: str, body: str, *, labels: tuple[str, ...] = ()) -> dict[str, object]:
    return {
        "action": action,
        "issue": {
            "number": 1149,
            "body": body,
            "title": "Synthetic correspondence fixture",
            "labels": [{"name": label} for label in labels],
            "html_url": "https://example.invalid/issues/1149",
            "created_at": "2026-09-15T00:00:00Z",
        },
        "repository": {"default_branch": "main"},
    }


def fetched_record(body: str = "Ordinary body.") -> dict[int, dict[str, object]]:
    return {
        1149: {
            "number": 1149,
            "state": "OPEN",
            "labels": {"nodes": []},
            "updatedAt": "2026-09-15T00:00:00Z",
            "body": body,
            "url": "https://example.invalid/issues/1149",
        }
    }


def run_event(document: dict[str, object], event_name: str) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as raw:
        event_path = Path(raw) / "event.json"
        event_path.write_text(json.dumps(document), encoding="utf-8")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            status = tracker_event_checks.grade_event_path(event_path, event_name)
    return status, stdout.getvalue()


class ALabelAdditionBindsTheTwoPublicHosts(unittest.TestCase):
    def test_in_flight_is_absent_at_the_hook_and_reported_by_the_event_host(self) -> None:
        row = correspondence.posture_row(
            "branch-in-flight",
            correspondence.Surface.BODY,
            correspondence.Trigger.LABEL_ADDED,
        )
        with mock.patch.object(tracker_publish_hook, "write_marker"):
            hook_result = tracker_publish_hook.handle(
                hook_payload("gh issue edit 1149 --add-label 'in flight'")
            )

        with tempfile.TemporaryDirectory() as raw:
            event_path = Path(raw) / "event.json"
            event_path.write_text(
                json.dumps(issue_event("labeled", "Ordinary body.", labels=("in flight",))),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = tracker_event_checks.grade_event_path(event_path, "issues")

        self.assertEqual({}, hook_result)
        self.assertEqual(1, status)
        self.assertNotIn("branch:in-flight", str(hook_result))
        self.assertIn("branch:in-flight", stdout.getvalue())
        self.assertEqual(
            correspondence.PostureCell(correspondence.Posture.ABSENT),
            row.hook_command,
        )
        self.assertEqual(
            correspondence.PostureCell(
                correspondence.Posture.REPORT,
                "branch:in-flight",
            ),
            row.changed_record,
        )


class TheDeclaredRowsCoverTheDerivedRulePopulation(unittest.TestCase):
    def test_every_rule_either_host_can_emit_has_a_row(self) -> None:
        self.assertEqual(frozenset(), correspondence.unnamed_rules())

    def test_a_planted_unnamed_rule_proves_the_walk_is_live(self) -> None:
        planted = (
            correspondence.hook_rule_population()
            | correspondence.event_rule_population()
            | {"synthetic:unnamed-rule"}
        )

        self.assertEqual(
            frozenset({"synthetic:unnamed-rule"}),
            correspondence.unnamed_rules(planted),
        )

    def test_posture_keys_and_writer_host_pairs_are_unique_and_complete(self) -> None:
        posture_keys = [
            (row.predicate, row.surface, row.trigger)
            for row in correspondence.POSTURE_ROWS
        ]
        reach_keys = [
            (row.writer, row.host) for row in correspondence.WRITER_REACH
        ]

        self.assertEqual(len(posture_keys), len(set(posture_keys)))
        self.assertEqual(len(reach_keys), len(set(reach_keys)))
        self.assertEqual(
            len(correspondence.Writer) * len(correspondence.Host),
            len(reach_keys),
        )

    def test_the_claude_section_points_at_each_object_and_copies_no_limit(self) -> None:
        text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        section = markdown_section(text, "### Tracker publication correspondence")

        self.assertIn("tracker_publication_correspondence.WRITER_REACH", section)
        self.assertIn("tracker_publication_correspondence.POSTURE_ROWS", section)
        self.assertIn("tracker_publication_correspondence.DECLARED_LIMITS", section)
        self.assertEqual((), bind(correspondence.DECLARED_LIMITS, section, mode=NAMING))

    def test_each_current_pairing_surface_points_at_the_objects_and_copies_no_row(self) -> None:
        claims = correspondence.prose_row_claims()
        for relative in correspondence.PAIRING_PROSE:
            with self.subTest(relative=relative):
                text = (REPO_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("tracker_publication_correspondence.WRITER_REACH", text)
                self.assertIn("tracker_publication_correspondence.POSTURE_ROWS", text)
                self.assertEqual((), bind(claims, text, mode=NAMING))

    def test_the_behavior_tests_cover_the_complete_condition_vocabulary(self) -> None:
        declared = {
            condition
            for row in correspondence.POSTURE_ROWS
            for host in correspondence.Host
            for condition, _posture in row.cell(host).conditions
        }
        self.assertEqual(set(correspondence.RuntimeCondition), declared)


class EveryBehaviorWriterReachRowCrossesItsPublicSeam(unittest.TestCase):
    def test_behavior_rows_are_the_four_driven_writer_host_pairs(self) -> None:
        expected = {
            (correspondence.Writer.PUBLISHER_COMMAND, correspondence.Host.HOOK_COMMAND),
            (correspondence.Writer.MAP_SESSION, correspondence.Host.DIRECT_WRITER),
            (correspondence.Writer.MERGE_RECEIPT, correspondence.Host.RECEIPT_PREPUBLICATION),
            (correspondence.Writer.HOURLY_MAP_REFRESH, correspondence.Host.DIRECT_WRITER),
        }
        declared = {
            (row.writer, row.host)
            for row in correspondence.WRITER_REACH
            if row.disposition is correspondence.EvidenceDisposition.BEHAVIOR
        }
        self.assertEqual(expected, declared)

        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(tracker_publish_hook, "current_index", return_value=(index, ())),
            mock.patch.object(tracker_publish_hook, "refresh_default_branch", return_value=True),
            mock.patch.object(tracker_publish_hook, "fetch_readback", return_value=fetched_record()),
            mock.patch.object(tracker_publish_hook, "write_marker"),
        ):
            hook = tracker_publish_hook.handle(
                hook_payload("gh issue comment 1149 --body 'Ordinary comment.'")
            )
            direct_issue = {
                "number": 1149,
                "body": "Ordinary body.",
                "labels": [],
                "url": "https://example.invalid/issues/1149",
            }
            map_session = tracker_publish_hook.authorize_issue_body(
                "Ordinary body.", "map session writer", issue=direct_issue
            )
            hourly = tracker_publish_hook.authorize_issue_body(
                "Ordinary body.", "hourly map refresh writer", issue=direct_issue
            )
        receipt_status, receipt = run_event(
            {
                **issue_event("created", "Ordinary body."),
                "comment": {
                    "body": "Ordinary comment.",
                    "html_url": "https://example.invalid/issues/1149#comment",
                },
            },
            "issue_comment",
        )

        self.assertTrue(hook)
        self.assertIn("scanned body", map_session)
        self.assertIn("scanned body", hourly)
        self.assertEqual(0, receipt_status)
        self.assertIn("Tracker PHI shape layer", receipt)


class EveryRuledTriggerIsDrivenAtBothHostBoundaries(unittest.TestCase):
    PHI_SHAPE = "123-45-6789"
    FILED = (
        "**Filed from:** ticket #1149 build, 2026-09-15.\n\n" + PHI_SHAPE
    )
    CASES = (
        (
            correspondence.Trigger.CREATE,
            "gh issue create --title 'Synthetic ticket' --body '"
            + FILED
            + "'",
            issue_event("opened", FILED),
            "issues",
            True,
            (
                "tracker_scan",
                "tracker_branch_scope",
                "tracker_bodies",
                "tracker_coordinates",
                "tracker_measurements",
                "tracker_filed_from",
            ),
        ),
        (
            correspondence.Trigger.BODY_EDIT,
            "gh issue edit 1149 --body '123-45-6789'",
            {
                **issue_event("edited", PHI_SHAPE),
                "changes": {"body": {"from": "Old body."}},
            },
            "issues",
            True,
            (
                "tracker_scan",
                "tracker_branch_scope",
                "tracker_bodies",
                "tracker_coordinates",
                "tracker_measurements",
                "tracker_filed_from",
            ),
        ),
        (
            correspondence.Trigger.TITLE_EDIT,
            "gh issue edit 1149 --title '123-45-6789'",
            {
                **issue_event("edited", "Ordinary body."),
                "issue": {
                    **issue_event("edited", "Ordinary body.")["issue"],
                    "title": PHI_SHAPE,
                },
                "changes": {"title": {"from": "Old title"}},
            },
            "issues",
            True,
            (
                "tracker_scan",
                "tracker_branch_scope",
                "tracker_bodies",
                "tracker_coordinates",
            ),
        ),
        (
            correspondence.Trigger.LABEL_ADDED,
            "gh issue edit 1149 --add-label bug",
            issue_event("labeled", PHI_SHAPE),
            "issues",
            False,
            ("tracker_scan", "tracker_branch_scope"),
        ),
        (
            correspondence.Trigger.LABEL_REMOVED,
            "gh issue edit 1149 --remove-label bug",
            issue_event("unlabeled", "Ordinary body."),
            "issues",
            False,
            (),
        ),
        (
            correspondence.Trigger.COMMENT,
            "gh issue comment 1149 --body '123-45-6789'",
            {
                **issue_event("created", "Ordinary issue body."),
                "comment": {
                    "body": PHI_SHAPE,
                    "html_url": "https://example.invalid/issues/1149#comment",
                },
            },
            "issue_comment",
            True,
            (
                "tracker_scan",
                "tracker_branch_scope",
                "tracker_bodies",
                "tracker_coordinates",
                "tracker_measurements",
            ),
        ),
        (
            correspondence.Trigger.REVIEW,
            "gh pr review 1149 --body '123-45-6789' --comment",
            {
                "action": "submitted",
                "pull_request": {
                    "number": 1149,
                    "body": "Ordinary pull request body.",
                    "title": "Synthetic pull request",
                    "labels": [],
                    "html_url": "https://example.invalid/pull/1149",
                },
                "review": {"body": PHI_SHAPE, "html_url": "https://example.invalid/review/1"},
            },
            "pull_request_review",
            True,
            (
                "tracker_scan",
                "tracker_branch_scope",
                "tracker_bodies",
                "tracker_coordinates",
                "tracker_measurements",
            ),
        ),
        (
            correspondence.Trigger.CLOSE,
            "gh issue close 1149",
            issue_event("closed", "Ordinary body."),
            "issues",
            False,
            (),
        ),
    )

    def test_each_trigger_is_built_once_as_a_command_and_an_event(self) -> None:
        index = phi_scan.build_index(set(), set())
        for trigger, command, document, event_name, hook_reached, expected_modules in self.CASES:
            with self.subTest(trigger=trigger):
                with (
                    mock.patch.object(tracker_publish_hook, "current_index", return_value=(index, ())),
                    mock.patch.object(tracker_publish_hook, "refresh_default_branch", return_value=True),
                    mock.patch.object(tracker_publish_hook, "fetch_readback", return_value=fetched_record()),
                    mock.patch.object(tracker_publish_hook, "write_marker"),
                ):
                    response = tracker_publish_hook.handle(hook_payload(command))

                calls: list[str] = []

                def runner(arguments, **_kwargs):
                    module = Path(arguments[1]).stem
                    calls.append(module)
                    return __import__("subprocess").CompletedProcess(arguments, 0, "clean\n", "")

                with tempfile.TemporaryDirectory() as raw:
                    path = Path(raw) / "event.json"
                    path.write_text(json.dumps(document), encoding="utf-8")
                    with contextlib.redirect_stdout(io.StringIO()):
                        tracker_event_checks.grade_event_path(
                            path, event_name, runner=runner
                        )

                self.assertEqual(hook_reached, bool(response))
                self.assertEqual(expected_modules, tuple(calls))
                if hook_reached:
                    self.assertIn("phi:ssn", str(response))
                if expected_modules:
                    status, report = run_event(document, event_name)
                    self.assertEqual(0, status)
                    self.assertIn("ssn", report)

    def test_a_bodyless_review_is_absent_at_both_hosts(self) -> None:
        command = "gh pr review 1149 --approve"
        document = {
            "action": "submitted",
            "pull_request": {
                "number": 1149,
                "body": "Ordinary pull request body.",
                "title": "Synthetic pull request",
                "labels": [],
                "html_url": "https://example.invalid/pull/1149",
            },
            "review": {"body": "", "html_url": "https://example.invalid/review/1"},
        }
        row = correspondence.posture_row(
            "no-publication-on-bodyless-review",
            correspondence.Surface.REVIEW,
            correspondence.Trigger.REVIEW,
        )
        self.assertEqual({}, tracker_publish_hook.handle(hook_payload(command)))
        status, report = run_event(document, "pull_request_review")
        self.assertEqual(0, status)
        self.assertEqual("", report)
        for host in correspondence.Host:
            self.assertEqual(correspondence.Posture.ABSENT, row.cell(host).posture)

    def test_label_removal_names_why_neither_host_runs(self) -> None:
        row = correspondence.posture_row(
            "no-publication-on-label-removal",
            correspondence.Surface.LABELS,
            correspondence.Trigger.LABEL_REMOVED,
        )

        self.assertEqual(
            "A removal only takes triggers away, and the named removal is an "
            "unwatched write no trigger reaches.",
            row.reason,
        )

    def test_branch_trigger_exclusions_and_label_title_are_observed(self) -> None:
        create_in_flight = correspondence.posture_row(
            "branch-in-flight",
            correspondence.Surface.BODY,
            correspondence.Trigger.CREATE,
        )
        self.assertEqual(correspondence.Posture.ABSENT, create_in_flight.hook_command.posture)
        self.assertEqual(correspondence.Posture.REPORT, create_in_flight.changed_record.posture)

        title_event = {
            **issue_event("edited", "Ordinary body.", labels=("in flight",)),
            "issue": {
                **issue_event("edited", "Ordinary body.", labels=("in flight",))["issue"],
                "title": "Ordinary title",
            },
            "changes": {"title": {"from": "Old title"}},
        }
        title_branch = correspondence.tracker_branch_scope.grade(title_event, "issues")
        self.assertIsNone(title_branch.verdict.rule)
        self.assertFalse(any(
            row.predicate == "branch-in-flight"
            and row.surface is correspondence.Surface.TITLE
            for row in correspondence.POSTURE_ROWS
        ))
        self.assertFalse(any(
            row.surface is correspondence.Surface.BODY
            and row.trigger is correspondence.Trigger.TITLE_EDIT
            for row in correspondence.POSTURE_ROWS
        ))
        title_edit_path = correspondence.posture_row(
            "branch-unresolved-path",
            correspondence.Surface.TITLE,
            correspondence.Trigger.TITLE_EDIT,
        )
        self.assertEqual(
            correspondence.Posture.REPORT,
            title_edit_path.changed_record.posture,
        )

        review_event = {
            "action": "submitted",
            "pull_request": {
                "number": 1149,
                "body": "Ordinary pull request body.",
                "title": "Synthetic pull request",
                "labels": [],
                "html_url": "https://example.invalid/pull/1149",
            },
            "review": {
                "body": "Done on this branch.",
                "html_url": "https://example.invalid/review/1",
            },
        }
        review_branch = correspondence.tracker_branch_scope.grade(
            review_event, "pull_request_review"
        )
        self.assertNotEqual("branch:self-declares-completion", review_branch.verdict.rule)
        self.assertFalse(any(
            row.predicate == "branch-self-declares-completion"
            and row.trigger is correspondence.Trigger.REVIEW
            for row in correspondence.POSTURE_ROWS
        ))

        label_event = issue_event("labeled", "Ordinary body.")
        label_event["issue"]["title"] = "123-45-6789"
        status, report = run_event(label_event, "issues")
        self.assertEqual(0, status)
        self.assertIn("ssn", report)
        title_label = correspondence.posture_row(
            "ssn", correspondence.Surface.TITLE, correspondence.Trigger.LABEL_ADDED
        )
        self.assertEqual(correspondence.Posture.REPORT, title_label.changed_record.posture)

    def test_every_event_cell_names_a_rule_selected_for_its_trigger_surface(self) -> None:
        event_inputs = {
            trigger: (document, event_name)
            for trigger, _command, document, event_name, _hook, _modules in self.CASES
        }
        vocabularies = {
            "tracker_scan": correspondence.tracker_scan.EVENT_RULES,
            "tracker_branch_scope": correspondence.tracker_branch_scope.BRANCH_RULES,
            "tracker_bodies": correspondence.tracker_bodies.KINDS,
            "tracker_coordinates": (correspondence.tracker_coordinates.UNANCHORED,),
            "tracker_measurements": correspondence.tracker_measurements.RULES,
            "tracker_filed_from": correspondence.tracker_filed_from.EVENT_RULES,
            "map_scan": correspondence.map_scan.EVENT_RULES,
        }
        owners = {
            rule: module
            for module, rules in vocabularies.items()
            for rule in rules
        }
        for row in correspondence.POSTURE_ROWS:
            document, event_name = event_inputs[row.trigger]
            if row.predicate == "implementation-map-producer-stamp":
                document = json.loads(json.dumps(document))
                document["issue"]["number"] = 596
            selected = {
                check.module
                for check in tracker_event_checks.select_checks(document, event_name)
            }
            for host in (
                correspondence.Host.CHANGED_RECORD,
                correspondence.Host.RECEIPT_PREPUBLICATION,
            ):
                cell = row.cell(host)
                if cell.rule is None:
                    continue
                with self.subTest(row=row.predicate, trigger=row.trigger, host=host):
                    self.assertEqual(correspondence.Posture.REPORT, cell.posture)
                    self.assertIn(owners[cell.rule], selected)

    def test_every_command_extraction_rule_denies_at_handle(self) -> None:
        for kind in correspondence.DECLARED_UNREADABLE_RULES:
            extracted = tracker_publish_hook.Extraction(
                ("issue", "edit"),
                1149,
                (),
                (tracker_publish_hook.Unreadable("body", kind, "synthetic"),),
                ("issue", "edit"),
            )
            with (
                self.subTest(kind=kind),
                mock.patch.object(tracker_publish_hook, "extract", return_value=extracted),
                mock.patch.object(tracker_publish_hook, "write_marker"),
            ):
                response = tracker_publish_hook.handle(hook_payload("gh issue edit 1149"))
                specific = response["hookSpecificOutput"]
                self.assertEqual("deny", specific["permissionDecision"])
                self.assertIn(kind, specific["additionalContext"])

        for kind in correspondence.DECLARED_UNCLASSIFIED_API_RULES:
            extracted = tracker_publish_hook.Extraction(
                ("api",),
                None,
                (),
                (),
                None,
                (tracker_publish_hook.UnclassifiedApiCall(kind, "synthetic endpoint"),),
            )
            with (
                self.subTest(kind=kind),
                mock.patch.object(tracker_publish_hook, "extract", return_value=extracted),
                mock.patch.object(tracker_publish_hook, "write_marker"),
            ):
                response = tracker_publish_hook.handle(hook_payload("gh api synthetic"))
                specific = response["hookSpecificOutput"]
                self.assertEqual("deny", specific["permissionDecision"])
                self.assertIn(kind, specific["additionalContext"])


class RuntimeConditionsQualifyPostureAtTheHostsIOSeams(unittest.TestCase):
    def setUp(self) -> None:
        self.index = phi_scan.build_index(set(), set())

    def hook(self, command: str, *, fetch_fresh: bool = True, readback=None) -> dict:
        readback_result = fetched_record() if readback is None else readback
        with (
            mock.patch.object(tracker_publish_hook, "current_index", return_value=(self.index, ())),
            mock.patch.object(tracker_publish_hook, "refresh_default_branch", return_value=fetch_fresh),
            mock.patch.object(tracker_publish_hook, "write_marker"),
            mock.patch.object(tracker_publish_hook, "fetch_readback", return_value=readback_result),
        ):
            return tracker_publish_hook.handle(hook_payload(command))

    def direct(self, body: str, *, fetch_fresh: bool = True, current: str = "Ordinary body.") -> str:
        issue = {
            "number": 1149,
            "body": current,
            "labels": [],
            "state": "OPEN",
            "html_url": "https://example.invalid/issues/1149",
        }
        with (
            mock.patch.object(tracker_publish_hook, "current_index", return_value=(self.index, ())),
            mock.patch.object(tracker_publish_hook, "refresh_default_branch", return_value=fetch_fresh),
        ):
            return tracker_publish_hook.authorize_issue_body(
                body, "synthetic direct writer", issue=issue
            )

    def test_a_synthetic_declaration_does_not_suppress_shape_grading(self) -> None:
        body = (
            "phi-scan: synthetic\n"
            "DOB: 01/02/2000\nMRN: 12345\n123-45-6789\n"
            "555-555-1212\n1/2/2026"
        )
        hook = self.hook(f"gh issue edit 1149 --body '{body}'")
        direct = self.direct(body)
        event = {
            **issue_event("edited", body),
            "changes": {"body": {"from": "Old body."}},
        }
        changed_status, changed = run_event(event, "issues")
        receipt_status, receipt = run_event(
            {
                **issue_event("created", "Ordinary body."),
                "comment": {
                    "body": body,
                    "html_url": "https://example.invalid/issues/1149#comment",
                },
            },
            "issue_comment",
        )
        rules = correspondence.DECLARED_EVENT_PHI_RULES
        self.assertEqual(0, changed_status)  # PHI is advisory at the event host.
        self.assertEqual(0, receipt_status)
        for rule in rules:
            with self.subTest(rule=rule):
                self.assertIn(f"advise: phi:{rule}", str(hook))
                self.assertIn(f"advise: phi:{rule}", direct)
                self.assertIn(rule, changed)
                self.assertIn(rule, receipt)
                row = correspondence.posture_row(
                    rule.removeprefix("phi-").replace(":", "-"),
                    correspondence.Surface.BODY,
                    correspondence.Trigger.BODY_EDIT,
                )
                receipt_row = correspondence.posture_row(
                    rule.removeprefix("phi-").replace(":", "-"),
                    correspondence.Surface.COMMENT,
                    correspondence.Trigger.COMMENT,
                )
                for cell in (
                    row.hook_command,
                    row.direct_writer,
                    row.changed_record,
                    receipt_row.receipt_prepublication,
                ):
                    self.assertEqual(
                        cell.posture,
                        cell.under(
                            correspondence.RuntimeCondition.SYNTHETIC_DECLARATION
                        ),
                    )

    def test_a_failed_fetch_changes_only_the_hook_side_unresolved_path_posture(self) -> None:
        missing = (
            "https://github.com/mshamblin5150-code/clinical-skills/blob/main/"
            "tools/definitely-not-present-1149.py"
        )
        body = f"See [missing]({missing})."
        hook = self.hook(f"gh issue edit 1149 --body '{body}'", fetch_fresh=False)
        direct = self.direct(body, fetch_fresh=False)
        event = {
            **issue_event("edited", body),
            "changes": {"body": {"from": "Old body."}},
        }
        _status, changed = run_event(event, "issues")
        _receipt_status, receipt = run_event(
            {
                **issue_event("created", "Ordinary body."),
                "comment": {
                    "body": body,
                    "html_url": "https://example.invalid/issues/1149#comment",
                },
            },
            "issue_comment",
        )
        row = correspondence.posture_row(
            "branch-unresolved-path",
            correspondence.Surface.BODY,
            correspondence.Trigger.BODY_EDIT,
        )
        receipt_row = correspondence.posture_row(
            "branch-unresolved-path",
            correspondence.Surface.COMMENT,
            correspondence.Trigger.COMMENT,
        )

        self.assertIn("advise: branch:unresolved-path", str(hook))
        self.assertIn("advise: branch:unresolved-path", direct)
        self.assertIn("branch:unresolved-path", changed)
        self.assertIn("branch:unresolved-path", receipt)
        self.assertEqual(
            correspondence.Posture.ADVISE,
            row.hook_command.under(correspondence.RuntimeCondition.FETCH_FAILED),
        )
        self.assertEqual(
            correspondence.Posture.REPORT,
            row.changed_record.under(correspondence.RuntimeCondition.FETCH_FAILED),
        )
        self.assertEqual(
            correspondence.Posture.REPORT,
            receipt_row.receipt_prepublication.under(
                correspondence.RuntimeCondition.FETCH_FAILED
            ),
        )

    def test_a_failed_readback_leaves_filed_from_ungraded_only_at_the_hook(self) -> None:
        current = "**Filed from:** ticket #1149's build, 2026-09-15.\n\nOld body."
        proposed = "Replacement body citing #1149."
        with (
            mock.patch.object(tracker_publish_hook, "current_index", return_value=(self.index, ())),
            mock.patch.object(tracker_publish_hook, "refresh_default_branch", return_value=True),
            mock.patch.object(tracker_publish_hook, "fetch_readback", side_effect=OSError("offline")),
            mock.patch.object(tracker_publish_hook, "write_marker"),
        ):
            hook = tracker_publish_hook.handle(
                hook_payload(f"gh issue edit 1149 --body '{proposed}'")
            )
        with self.assertRaisesRegex(ValueError, "filed-from:edit") as refused:
            self.direct(proposed, current=current)
        direct = str(refused.exception)
        event = {
            **issue_event("edited", proposed),
            "changes": {"body": {"from": current}},
        }
        _status, changed = run_event(event, "issues")
        _receipt_status, receipt = run_event(
            {
                **issue_event("created", "Ordinary body."),
                "comment": {
                    "body": proposed,
                    "html_url": "https://example.invalid/issues/1149#comment",
                },
            },
            "issue_comment",
        )
        row = correspondence.posture_row(
            "filed-from-preservation",
            correspondence.Surface.BODY,
            correspondence.Trigger.BODY_EDIT,
        )
        comment_row = correspondence.posture_row(
            "filed-from-not-graded-on-comment",
            correspondence.Surface.COMMENT,
            correspondence.Trigger.COMMENT,
        )

        self.assertNotIn("filed-from:edit", str(hook))
        self.assertIn("filed-from:edit", direct)
        self.assertIn("filed-from:edited", changed)
        self.assertNotIn("filed-from:", receipt)
        self.assertEqual(
            correspondence.Posture.ABSENT,
            row.hook_command.under(correspondence.RuntimeCondition.READBACK_FAILED),
        )
        self.assertEqual(
            correspondence.Posture.REPORT,
            row.changed_record.under(correspondence.RuntimeCondition.READBACK_FAILED),
        )
        self.assertEqual(
            correspondence.Posture.ABSENT,
            comment_row.receipt_prepublication.under(
                correspondence.RuntimeCondition.READBACK_FAILED
            ),
        )


class EveryHookAnalysisRuleKeepsItsDeclaredPosture(unittest.TestCase):
    def test_the_complete_analysis_vocabulary_agrees_with_the_table(self) -> None:
        marker = "salted-correspondence-marker-1149"
        fixtures = {
            "phi:corpus-name": (marker, phi_scan.build_index({marker}, set()), None, None),
            "phi:corpus-date": (
                marker + " 09/09/2026",
                phi_scan.build_index(set(), {"09/09/2026"}),
                None,
                None,
            ),
            "phi:dob-with-date": (marker + " DOB: 01/02/2000", None, None, None),
            "phi:mrn-with-digits": (marker + " MRN: 12345", None, None, None),
            "phi:ssn": (marker + " 123-45-6789", None, None, None),
            "phi:phone": (marker + " 555-555-1212", None, None, None),
            "phi:us-short-date": (marker + " 1/2/2026", None, None, None),
            "body:lost-at-dash": ("@-", None, None, None),
            "body:empty-body": ("", None, None, None),
            "body:literal-at-path": ("@body.md", None, None, None),
            "body:double-encoded": ("before â€” after", None, None, None),
            "body:c0-control-character": (marker + "\bdamaged", None, None, None),
            "body:carriage-return-flanked": (marker + "\rflanked", None, None, None),
            "body:literal-newline-escape": (marker + r"\nliteral", None, None, None),
            "body:doubled-path-separator": (marker + r" C:\\folder", None, None, None),
            "coordinate:unanchored": (marker + " tools/example.py:12", None, None, None),
            "verdict:missing-discriminator": (
                marker + "\n**Verdict:** HOLDS",
                None,
                None,
                None,
            ),
            "citation:retired-correction-rule": (
                marker
                + " on #436's ruling: a correction below the advice is not a correction "
                "for anyone who acts on the advice.",
                None,
                None,
                None,
            ),
            "branch:repo-relative-link": (marker + " [x](docs/x.md)", None, None, None),
            "branch:near-miss": (
                marker
                + " https://github.com/example/repo/blob/main/docs/adr/0083-not-the-real-slug.md",
                None,
                None,
                None,
            ),
            "branch:unresolved-path": (
                marker
                + " https://github.com/example/repo/blob/main/docs/adr/9999-not-on-main.md",
                None,
                None,
                None,
            ),
            "branch:self-declares-completion": (
                "Built on a branch. " + marker,
                None,
                None,
                None,
            ),
            "branch:in-flight": (
                marker + " ordinary",
                None,
                {"number": 1149, "labels": ["in flight"]},
                None,
            ),
            "branch:blockquote-missing": (
                "**Branch state:** `ticket-1149` at `"
                + "a" * 40
                + "` is not on `main` as of `2026-09-15`.\n"
                + marker,
                None,
                {"number": 1149, "labels": ["in flight"]},
                None,
            ),
            "branch:ancestry-refused": (
                "> **Branch state:** this text rests on `main` at `"
                + "a" * 40
                + "` as of `2026-09-15`.\n"
                + marker,
                None,
                {"number": 1149, "labels": ["in flight"]},
                False,
            ),
        }
        observed: dict[str, str] = {}
        for rule, (body, custom_index, issue, ancestry) in fixtures.items():
            ancestry_patch = (
                mock.patch.object(
                    tracker_publish_hook.tracker_branch_scope,
                    "_main_ancestry",
                    return_value=ancestry,
                )
                if ancestry is not None
                else contextlib.nullcontext()
            )
            with ancestry_patch:
                analysis = tracker_publish_hook.analyze(
                    tracker_publish_hook.Publication("body", body),
                    index=custom_index or self.empty_index(),
                    issue=issue,
                    remote_fresh=True,
                )
            observed[rule] = next(
                finding.posture for finding in analysis.findings if finding.rule == rule
            )

        self.assertEqual(set(tracker_publish_hook.REDACTION_WALK_KINDS), set(observed))
        for rule, posture in observed.items():
            with self.subTest(rule=rule):
                declared = {
                    row.hook_command.posture.value
                    for row in correspondence.POSTURE_ROWS
                    if row.hook_command.rule == rule
                }
                self.assertEqual({posture}, declared)

    @staticmethod
    def empty_index():
        return phi_scan.build_index(set(), set())


if __name__ == "__main__":
    unittest.main()
