"""Tests for the pre-publish tracker hook.

phi-scan: synthetic

Every identifier-shaped value in this file is invented. The tests exercise the
hook's public command and JSON boundaries; they do not publish tracker text.
"""

from __future__ import annotations

import unittest
import tempfile
import io
import json
import contextlib
import sys
from pathlib import Path
from unittest import mock

import tracker_publish_hook as hook
import phi_scan


class TheRecognizedPublishSetIsDeclared(unittest.TestCase):
    def test_every_ruled_command_family_is_named(self) -> None:
        self.assertEqual(
            hook.PUBLISH_ROUTES,
            (
                ("issue", "create"),
                ("issue", "comment"),
                ("issue", "edit"),
                ("issue", "close"),
                ("pr", "create"),
                ("pr", "comment"),
                ("pr", "edit"),
                ("pr", "review"),
                ("api",),
            ),
        )


class InlineTrackerTextIsRead(unittest.TestCase):
    def test_title_and_body_are_separate_publication_fields(self) -> None:
        result = hook.extract(
            'gh issue edit 670 --title "A revised title" --body "The revised body"'
        )

        self.assertEqual(result.route, ("issue", "edit"))
        self.assertEqual(result.number, 670)
        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("title", "A revised title"), ("body", "The revised body")],
        )
        self.assertEqual(result.unreadable, ())

    def test_api_write_fields_are_publications_and_carry_the_record_number(self) -> None:
        result = hook.extract(
            "gh api repos/example/project/issues/670/comments "
            "-f body='API comment' -f title='API title'"
        )

        self.assertEqual(result.route, ("api",))
        self.assertEqual(result.number, 670)
        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("body", "API comment"), ("title", "API title")],
        )

    def test_issue_urls_and_the_close_comment_short_flag_are_read(self) -> None:
        result = hook.extract(
            "gh issue close https://github.com/example/project/issues/670 "
            "-c 'Closing comment'"
        )

        self.assertEqual(result.number, 670)
        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("body", "Closing comment")],
        )

    def test_issue_close_comment_equals_forms_are_read(self) -> None:
        long_form = hook.extract(
            "gh issue close 670 --comment='Closing text'"
        )
        short_form = hook.extract(
            "gh issue close 670 -c='Other closing text'"
        )

        self.assertEqual(
            [(row.field, row.text) for row in long_form.publications],
            [("body", "Closing text")],
        )
        self.assertEqual(
            [(row.field, row.text) for row in short_form.publications],
            [("body", "Other closing text")],
        )

    def test_plain_inline_variables_are_resolved_before_scanning(self) -> None:
        result = hook.extract(
            "BODY='Expanded tracker text'; "
            'gh issue comment 670 --body "$BODY"'
        )

        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("body", "Expanded tracker text")],
        )

    def test_numeric_create_fields_are_not_guessed_to_be_record_numbers(self) -> None:
        result = hook.extract(
            "gh issue create --title 670 --body 'A new issue body'"
        )

        self.assertIsNone(result.number)

    def test_option_first_targets_and_pull_request_urls_are_read(self) -> None:
        option_first = hook.extract(
            "gh issue comment --repo example/project 670 --body 'A comment'"
        )
        pull_url = hook.extract(
            "gh pr edit https://github.com/example/project/pull/706 "
            "--body 'A pull request body'"
        )

        self.assertEqual(option_first.number, 670)
        self.assertEqual(pull_url.number, 706)

    def test_numeric_option_values_are_not_record_targets(self) -> None:
        result = hook.extract(
            "gh issue edit --milestone 123 670 --body 'Edited body'"
        )

        self.assertEqual(result.number, 670)

    def test_pr_review_comment_switch_is_not_read_as_comment_text(self) -> None:
        result = hook.extract(
            "gh pr review --comment 706 --body 'Review body'"
        )

        self.assertEqual(result.number, 706)
        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("body", "Review body")],
        )

    def test_api_endpoint_preserves_the_record_operation_for_grading(self) -> None:
        result = hook.extract(
            "gh api --method PATCH repos/example/project/issues/670 "
            "-f body='Built on a branch.'"
        )

        self.assertEqual(result.route, ("api",))
        self.assertEqual(result.grade_route, ("issue", "edit"))

    def test_api_collection_endpoints_use_create_semantics(self) -> None:
        issue = hook.extract(
            "gh api repos/example/project/issues "
            "-f title='Issue' -f body='Built on a branch.'"
        )
        pull = hook.extract(
            "gh api repos/example/project/pulls "
            "-f title='Pull request' -f body='Built on a branch.'"
        )

        self.assertEqual(issue.grade_route, ("issue", "create"))
        self.assertEqual(pull.grade_route, ("pr", "create"))


class FileBackedTrackerTextIsRead(unittest.TestCase):
    def test_a_literal_body_file_is_read_and_named(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "issue.md"
            body.write_text("File-backed body", encoding="utf-8")

            result = hook.extract(f'gh issue comment 670 --body-file "{body}"')

        self.assertEqual(
            [(row.field, row.text, row.source) for row in result.publications],
            [("body", "File-backed body", str(body))],
        )
        self.assertEqual(result.unreadable, ())

    def test_api_file_and_json_input_forms_are_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            body = root / "body.md"
            body.write_text("API file body", encoding="utf-8")
            document = root / "request.json"
            document.write_text(
                json.dumps({"title": "Input title", "body": "Input body"}),
                encoding="utf-8",
            )

            field_result = hook.extract(
                f'gh api repos/example/project/issues/670 -F body="@{body}"'
            )
            input_result = hook.extract(
                f'gh api repos/example/project/issues/670 --input "{document}"'
            )
            equals_result = hook.extract(
                f'gh issue comment 670 --body-file="{body}"'
            )
            raw_at_result = hook.extract(
                "gh api repos/example/project/issues/670 -f body='@literal text'"
            )

        self.assertEqual(
            [(row.field, row.text) for row in field_result.publications],
            [("body", "API file body")],
        )
        self.assertEqual(
            [(row.field, row.text) for row in input_result.publications],
            [("title", "Input title"), ("body", "Input body")],
        )
        self.assertEqual(
            [(row.field, row.text) for row in equals_result.publications],
            [("body", "API file body")],
        )
        self.assertEqual(
            [(row.field, row.text) for row in raw_at_result.publications],
            [("body", "@literal text")],
        )

    def test_api_json_can_arrive_in_an_inline_heredoc(self) -> None:
        command = (
            "gh api repos/example/project/issues/670 --input - <<'JSON'\n"
            '{"body": "Heredoc API body"}\n'
            "JSON\n"
        )

        result = hook.extract(command)

        self.assertEqual(
            [(row.field, row.text, row.source) for row in result.publications],
            [("body", "Heredoc API body", "inline heredoc")],
        )


class UnreadableTrackerTextIsClassified(unittest.TestCase):
    def test_each_ruled_residue_has_its_own_class(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            absent = Path(temporary) / "not-written.md"
            commands = {
                "missing-file": f'gh issue comment 670 --body-file "{absent}"',
                "external-variable": 'gh issue comment 670 --body-file "$BODY_PATH"',
                "pipe": "printf text | gh issue comment 670 --body-file -",
                "written-before-publish": (
                    f'printf text > "{absent}"; '
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "command-substitution": (
                    'BODY_PATH="$(make-body)"; '
                    'gh issue comment 670 --body-file "$BODY_PATH"'
                ),
            }

            actual = {
                name: hook.extract(command).unreadable[0].kind
                for name, command in commands.items()
            }

        self.assertEqual(actual, {name: name for name in commands})

    def test_an_inline_heredoc_is_read_from_the_command(self) -> None:
        command = (
            "gh issue create --title 'Ticket' --body-file - <<'BODY'\n"
            "First line\nSecond line\n"
            "BODY\n"
        )

        result = hook.extract(command)

        self.assertEqual(
            [(row.field, row.text, row.source) for row in result.publications],
            [
                ("title", "Ticket", "inline"),
                ("body", "First line\nSecond line", "inline heredoc"),
            ],
        )
        self.assertEqual(result.unreadable, ())


class PublishedFieldsAreGradedWithoutEchoingThem(unittest.TestCase):
    def test_phi_findings_are_advisory_counts_with_rule_and_field(self) -> None:
        invented = "Jordan Vance"
        index = phi_scan.build_index({invented}, set())

        result = hook.analyze(
            hook.Publication("body", f"Seen by {invented}"),
            index=index,
            issue=None,
            remote_fresh=True,
        )

        self.assertEqual(
            [(row.rule, row.count, row.field, row.posture) for row in result.findings],
            [("phi:corpus-name", 1, "body", "advise")],
        )
        self.assertNotIn(invented, result.report)
        self.assertIn("context-blind", result.report)

    def test_branch_scope_posture_is_decided_per_trigger(self) -> None:
        index = phi_scan.build_index(set(), set())
        existing_prefix = (
            "https://github.com/example/project/blob/main/docs/adr/"
            "0083-not-the-real-slug.md"
        )
        missing = (
            "https://github.com/example/project/blob/main/docs/adr/"
            "9999-not-on-main.md"
        )
        cases = (
            ("repo relative", "[record](docs/adr/0083.md)", None, True, "deny"),
            (
                "in flight",
                "Ordinary body",
                {"number": 670, "labels": ["in flight"]},
                True,
                "deny",
            ),
            ("completion", "Built on a branch.", None, True, "deny"),
            ("unresolved fresh", missing, None, True, "deny"),
            ("unresolved degraded", missing, None, False, "advise"),
            ("near miss fresh", existing_prefix, None, True, "advise"),
        )

        for label, text, issue, remote_fresh, posture in cases:
            with self.subTest(label=label):
                result = hook.analyze(
                    hook.Publication("body", text),
                    index=index,
                    issue=issue,
                    remote_fresh=remote_fresh,
                )
                branch = [row for row in result.findings if row.rule.startswith("branch:")]
                self.assertEqual([row.posture for row in branch], [posture])

    def test_an_in_flight_label_does_not_make_a_title_banner_mandatory(self) -> None:
        result = hook.analyze(
            hook.Publication("title", "A revised issue title"),
            index=phi_scan.build_index(set(), set()),
            issue={"number": 670, "labels": ["in flight"]},
            remote_fresh=True,
        )

        self.assertEqual(
            [row for row in result.findings if row.rule.startswith("branch:")],
            [],
        )
        self.assertIn("title path triggers", result.report)

    def test_completion_is_a_comment_trigger_not_an_issue_body_trigger(self) -> None:
        index = phi_scan.build_index(set(), set())
        issue = {"number": 670, "labels": []}
        body_edit = hook.analyze(
            hook.Publication("body", "Built on a branch."),
            index=index,
            issue=issue,
            remote_fresh=True,
            route=("issue", "edit"),
        )
        comment = hook.analyze(
            hook.Publication("body", "Built on a branch."),
            index=index,
            issue=issue,
            remote_fresh=True,
            route=("issue", "comment"),
        )

        self.assertEqual(
            [row for row in body_edit.findings if row.rule.startswith("branch:")],
            [],
        )
        self.assertEqual(
            [row.rule for row in comment.findings if row.rule.startswith("branch:")],
            ["branch:self-declares-completion"],
        )


class TheHookProtocolReportsOnlyPublishInvocations(unittest.TestCase):
    @staticmethod
    def payload(command: str) -> dict:
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }

    def test_a_nonpublishing_gh_invocation_is_silent(self) -> None:
        self.assertEqual(
            hook.handle(self.payload("gh issue edit 670 --add-label bug")),
            {},
        )

    def test_recognized_malformed_publications_are_loud(self) -> None:
        missing_value = hook.handle(
            self.payload("gh issue comment 670 --body")
        )
        broken_quote = hook.handle(
            self.payload("gh issue comment 670 --body 'unfinished")
        )

        for response in (missing_value, broken_quote):
            report = response["hookSpecificOutput"]["additionalContext"]
            self.assertIn("Unreadable body", report)
            self.assertNotIn("0 findings", report)

    def test_an_invalid_malformed_route_is_not_promoted_to_a_publish_route(self) -> None:
        response = hook.handle(
            self.payload("gh issue review 670 --body 'unfinished")
        )

        self.assertEqual(response, {})

    def test_a_clean_publish_is_allowed_and_names_what_was_read(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_issue",
                return_value={"number": 670, "labels": [], "url": "draft record"},
            ),
            mock.patch.object(hook, "write_marker") as write_marker,
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body 'Ordinary body'")
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["hookEventName"], "PreToolUse")
        self.assertNotIn("permissionDecision", specific)
        self.assertIn("body read from inline", specific["additionalContext"])
        self.assertIn("0 findings", specific["additionalContext"])
        write_marker.assert_called_once_with()

    def test_an_api_issue_edit_uses_issue_body_not_comment_rules(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_issue",
                return_value={"number": 670, "labels": [], "url": "draft record"},
            ),
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload(
                    "gh api --method PATCH repos/example/project/issues/670 "
                    "-f body='Built on a branch.'"
                )
            )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn("0 findings", specific["additionalContext"])

    def test_an_in_flight_scope_finding_denies_but_phi_only_advises(self) -> None:
        invented = "Jordan Vance"
        index = phi_scan.build_index({invented}, set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "write_marker"),
        ):
            with mock.patch.object(
                hook,
                "fetch_issue",
                return_value={"number": 670, "labels": ["in flight"]},
            ):
                denied = hook.handle(
                    self.payload("gh issue comment 670 --body 'Ordinary body'")
                )
            with mock.patch.object(
                hook,
                "fetch_issue",
                return_value={"number": 670, "labels": []},
            ):
                advised = hook.handle(
                    self.payload(
                        f"gh issue comment 670 --body 'Seen by {invented}'"
                    )
                )

        self.assertEqual(
            denied["hookSpecificOutput"]["permissionDecision"], "deny"
        )
        self.assertIn(
            "branch:in-flight",
            denied["hookSpecificOutput"]["additionalContext"],
        )
        self.assertNotIn("permissionDecision", advised["hookSpecificOutput"])
        advised_report = advised["hookSpecificOutput"]["additionalContext"]
        self.assertIn("phi:corpus-name", advised_report)
        self.assertNotIn(invented, advised_report)

    def test_unreadable_and_crashed_runs_are_loud_and_distinct(self) -> None:
        unreadable = hook.handle(
            self.payload('gh issue comment 670 --body-file "$OUTSIDE"')
        )
        crashed = hook.handle(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 42},
            }
        )

        unreadable_report = unreadable["hookSpecificOutput"]["additionalContext"]
        crashed_report = crashed["hookSpecificOutput"]["additionalContext"]
        self.assertIn("external-variable", unreadable_report)
        self.assertIn("--text <path>", unreadable_report)
        self.assertNotIn("HOOK FAILURE", unreadable_report)
        self.assertIn("HOOK FAILURE", crashed_report)
        self.assertIn("Unreadable body", crashed_report)

    def test_the_hook_marker_is_dated_and_contains_no_tracker_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marker = Path(temporary) / "marker.json"
            with mock.patch.object(hook, "PUBLISH_MARKER", marker):
                hook.write_marker()

            document = json.loads(marker.read_text(encoding="utf-8"))

        self.assertEqual(set(document), {"version", "ran_on"})
        self.assertEqual(document["version"], 1)
        self.assertRegex(document["ran_on"], r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")

    def test_the_command_reads_and_writes_the_hook_json_protocol(self) -> None:
        stdin = io.StringIO(json.dumps(self.payload("gh issue view 670")))
        stdout = io.StringIO()
        with (
            mock.patch.object(sys, "stdin", stdin),
            contextlib.redirect_stdout(stdout),
        ):
            status = hook.main([])

        self.assertEqual(status, 0)
        self.assertEqual(json.loads(stdout.getvalue()), {})

    def test_the_manual_text_command_fulfills_the_unreadable_remedy(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "body.md"
            body.write_text("[record](docs/adr/0083.md)", encoding="utf-8")
            stdout = io.StringIO()
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(hook, "refresh_default_branch", return_value=True),
                contextlib.redirect_stdout(stdout),
            ):
                status = hook.main(["--text", str(body)])

        self.assertEqual(status, 1)
        self.assertIn("branch:repo-relative-link", stdout.getvalue())
        self.assertNotIn("[record]", stdout.getvalue())


class ProjectSettingsRegisterTheHook(unittest.TestCase):
    def test_the_cost_guard_is_not_the_publish_route_list(self) -> None:
        path = Path(__file__).resolve().parent.parent / ".claude" / "settings.json"
        settings = json.loads(path.read_text(encoding="utf-8"))

        registrations = settings["hooks"]["PreToolUse"]
        self.assertEqual(len(registrations), 1)
        self.assertEqual(registrations[0]["matcher"], "Bash")
        self.assertEqual(
            registrations[0]["hooks"],
            [
                {
                    "type": "command",
                    "if": "Bash(gh *)",
                    "command": "python \"$CLAUDE_PROJECT_DIR/tools/tracker_publish_hook.py\"",
                    "timeout": 30,
                }
            ],
        )

    def test_a_plain_same_command_variable_is_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "comment.md"
            body.write_text("Assigned body", encoding="utf-8")
            command = (
                f'BODY_PATH="{body}"; '
                'gh issue comment 670 --body-file "$BODY_PATH"'
            )

            result = hook.extract(command)

        self.assertEqual(
            [(row.field, row.text, row.source) for row in result.publications],
            [("body", "Assigned body", str(body))],
        )
        self.assertEqual(result.unreadable, ())


if __name__ == "__main__":
    unittest.main()
