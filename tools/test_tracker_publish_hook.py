"""Tests for the pre-publish tracker hook.

phi-scan: synthetic

Every identifier-shaped value in this file is invented. The tests exercise the
hook's public command and JSON boundaries; they do not publish tracker text.
"""

from __future__ import annotations

import unittest
from pathlib import Path
import tempfile
import io
import json
import contextlib
import sys
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import tracker_publish_hook as hook
import phi_scan


def fetched_records(number: int, labels: tuple[str, ...] = ()) -> dict:
    """Return one complete invented GraphQL record keyed by its request number."""
    return {
        number: {
            "number": number,
            "state": "OPEN",
            "labels": {"nodes": [{"name": label} for label in labels]},
            "updatedAt": "2026-09-01T12:34:56Z",
            "body": "invented record body",
            "url": f"https://github.com/example/project/issues/{number}",
        }
    }


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


class DirectTrackerWritersCrossTheBodyGate(unittest.TestCase):
    def test_every_ruled_body_shape_is_refused(self) -> None:
        for body in (
            "@-",
            "word\bword",
            "before\rafter",
            r"before\nafter",
            r"open D:\\folder",
        ):
            with self.subTest(body=repr(body)):
                with self.assertRaisesRegex(ValueError, "tracker body refused"):
                    hook.authorize_issue_body(body, "map", issue_number=596)

    def test_a_map_body_without_a_producer_stamp_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "producer stamp"):
            hook.authorize_issue_body(
                "A complete tracker body.", "map", issue_number=596
            )

    def test_an_ordinary_non_map_body_is_accepted(self) -> None:
        hook.authorize_issue_body(
            "A complete tracker body.", "issue #596", issue_number=595
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

    def test_a_partial_body_file_uses_the_literal_cd_not_the_hook_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            body = root / "scratch" / "body.md"
            body.parent.mkdir()
            body.write_text("Command-rooted body", encoding="utf-8")
            with tempfile.TemporaryDirectory() as hook_directory:
                with contextlib.chdir(hook_directory):
                    result = hook.extract(
                        f'cd "{root}" && gh issue comment 670 '
                        '--body-file scratch/body.md'
                    )

        self.assertEqual(
            [(row.field, row.text, Path(row.source)) for row in result.publications],
            [("body", "Command-rooted body", body)],
        )
        self.assertEqual(result.unreadable, ())

    def test_the_last_literal_absolute_cd_wins(self) -> None:
        with tempfile.TemporaryDirectory() as first_directory:
            with tempfile.TemporaryDirectory() as last_directory:
                first = Path(first_directory)
                last = Path(last_directory)
                body = last / "body.md"
                body.write_text("Last folder body", encoding="utf-8")

                result = hook.extract(
                    f'cd "{first}" && cd "{last}" && '
                    'gh issue comment 670 --body-file body.md'
                )

        self.assertEqual(result.publications[0].text, "Last folder body")
        self.assertEqual(Path(result.publications[0].source), body)

    def test_a_later_unreadable_cd_invalidates_an_earlier_absolute_one(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            body = root / "body.md"
            body.write_text("Wrong file if read", encoding="utf-8")

            result = hook.extract(
                f'cd "{root}" && cd child && '
                'gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_a_later_absolute_cd_recovers_after_an_unreadable_one(self) -> None:
        with tempfile.TemporaryDirectory() as last_directory:
            last = Path(last_directory)
            body = last / "body.md"
            body.write_text("Recovered root", encoding="utf-8")

            result = hook.extract(
                f'cd child && cd "{last}" && '
                'gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications[0].text, "Recovered root")

    def test_a_pipeline_cd_never_roots_the_publish_command(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            (root / "body.md").write_text("Wrong pipeline file", encoding="utf-8")

            result = hook.extract(
                f'cd "{root}" | gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_an_unparseable_later_cd_invalidates_an_earlier_root(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            (root / "body.md").write_text("Wrong substituted file", encoding="utf-8")

            result = hook.extract(
                f'cd "{root}" && cd $(printf child) && '
                'gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_a_quoted_separator_inside_the_folder_is_literal(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory) / "A&B"
            root.mkdir()
            (root / "body.md").write_text("Quoted separator", encoding="utf-8")

            result = hook.extract(
                f'cd "{root}" && gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications[0].text, "Quoted separator")

    def test_a_cd_after_a_background_command_can_establish_the_root(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            (root / "body.md").write_text("Foreground cd", encoding="utf-8")

            result = hook.extract(
                f'noop & cd "{root}" && '
                'gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications[0].text, "Foreground cd")

    def test_unrelated_pipeline_and_redirection_preserve_the_root(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            (root / "body.md").write_text("Preserved root", encoding="utf-8")

            result = hook.extract(
                f'cd "{root}"; producer 2>&1 | consumer && '
                'gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications[0].text, "Preserved root")

    def test_quoted_fake_gh_does_not_hide_the_real_publication(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            (root / "body.md").write_text("Real publication", encoding="utf-8")

            result = hook.extract(
                f'printf "; gh issue edit 1" && cd "{root}" && '
                'gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications[0].text, "Real publication")

    def test_a_conditionally_skipped_cd_is_not_used_after_a_semicolon(self) -> None:
        with tempfile.TemporaryDirectory() as first_directory:
            with tempfile.TemporaryDirectory() as skipped_directory:
                first = Path(first_directory)
                skipped = Path(skipped_directory)
                (skipped / "body.md").write_text("Skipped file", encoding="utf-8")

                result = hook.extract(
                    f'cd "{first}" && gate && cd "{skipped}"; '
                    'gh issue comment 670 --body-file body.md'
                )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_an_or_conditional_cd_is_never_assumed_to_have_run(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            (root / "body.md").write_text("Conditionally skipped", encoding="utf-8")

            result = hook.extract(
                f'true || cd "{root}" && '
                'gh issue comment 670 --body-file body.md'
            )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_comments_and_heredocs_cannot_impersonate_the_publication(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            (root / "body.md").write_text("Actual body", encoding="utf-8")
            commands = (
                "# gh issue edit 1\n"
                f'cd "{root}" && gh issue comment 670 --body-file body.md',
                "python - <<'PY'\n"
                "gh issue edit 1\n"
                "PY\n"
                f'cd "{root}" && gh issue comment 670 --body-file body.md',
            )

            results = [hook.extract(command) for command in commands]

        self.assertEqual(
            [result.publications[0].text for result in results],
            ["Actual body", "Actual body"],
        )

    def test_a_noncommand_gh_argument_cannot_impersonate_the_publication(self) -> None:
        with tempfile.TemporaryDirectory() as first_directory:
            with tempfile.TemporaryDirectory() as real_directory:
                first = Path(first_directory)
                real = Path(real_directory)
                (first / "body.md").write_text("Wrong body", encoding="utf-8")
                (real / "body.md").write_text("Real body", encoding="utf-8")

                result = hook.extract(
                    f'cd "{first}"; printf "%s" gh issue comment 1 '
                    f'--body-file body.md; cd "{real}"; '
                    'gh issue comment 670 --body-file body.md'
                )

        self.assertEqual(result.publications[0].text, "Real body")

    def test_a_grouped_cd_is_refused_instead_of_reusing_an_outer_root(self) -> None:
        with tempfile.TemporaryDirectory() as outer_directory:
            with tempfile.TemporaryDirectory() as grouped_directory:
                outer = Path(outer_directory)
                grouped = Path(grouped_directory)
                (outer / "body.md").write_text("Wrong outer body", encoding="utf-8")
                (grouped / "body.md").write_text("Grouped body", encoding="utf-8")

                commands = (
                    f'cd "{outer}"; ( cd "{grouped}" && '
                    'gh issue comment 670 --body-file body.md )',
                    f'cd "{outer}"; (cd "{grouped}" && '
                    'gh issue comment 670 --body-file body.md )',
                )
                results = [hook.extract(command) for command in commands]

        self.assertEqual([result.publications for result in results], [(), ()])
        self.assertEqual(
            [result.unreadable[0].kind for result in results],
            ["unrooted-path", "unrooted-path"],
        )

    def test_a_cd_inside_control_flow_is_refused_as_unrootable(self) -> None:
        with tempfile.TemporaryDirectory() as outer_directory:
            with tempfile.TemporaryDirectory() as conditional_directory:
                outer = Path(outer_directory)
                conditional = Path(conditional_directory)
                (conditional / "body.md").write_text(
                    "Skipped conditional body", encoding="utf-8"
                )

                result = hook.extract(
                    f'cd "{outer}"; if false; then\ncd "{conditional}"\nfi\n'
                    'gh issue comment 670 --body-file body.md'
                )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_bounded_shell_wrappers_still_reach_the_publication(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            body = Path(command_directory) / "body.md"
            body.write_text("Wrapped publication", encoding="utf-8")
            commands = (
                f'command gh issue comment 670 --body-file "{body}"',
                f'env MODE=test gh issue comment 670 --body-file "{body}"',
            )

            results = [hook.extract(command) for command in commands]

        self.assertEqual(
            [result.publications[0].text for result in results],
            ["Wrapped publication", "Wrapped publication"],
        )

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

    def test_a_partial_api_input_uses_the_literal_cd(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            document = root / "request.json"
            document.write_text(
                json.dumps({"body": "Rooted input body"}), encoding="utf-8"
            )
            with tempfile.TemporaryDirectory() as hook_directory:
                with contextlib.chdir(hook_directory):
                    result = hook.extract(
                        f'cd "{root}" && gh api repos/example/project/issues/670 '
                        '--input request.json'
                    )

        self.assertEqual(
            [(row.field, row.text, Path(row.source)) for row in result.publications],
            [("body", "Rooted input body", document)],
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

    def test_a_partial_path_without_a_readable_cd_is_unrooted(self) -> None:
        with tempfile.TemporaryDirectory() as hook_directory:
            body = Path(hook_directory) / "body.md"
            body.write_text("Must not be read from the hook cwd", encoding="utf-8")
            with contextlib.chdir(hook_directory):
                without_cd = hook.extract(
                    "gh issue comment 670 --body-file body.md"
                )
                unreadable_cd = hook.extract(
                    'cd "$ROOT" && gh issue comment 670 --body-file body.md'
                )

        self.assertEqual(without_cd.publications, ())
        self.assertEqual(without_cd.unreadable[0].kind, "unrooted-path")
        self.assertEqual(unreadable_cd.publications, ())
        self.assertEqual(unreadable_cd.unreadable[0].kind, "unrooted-path")

    def test_a_drive_relative_path_is_never_joined_to_another_drive(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            result = hook.extract(
                f'cd "{command_directory}" && '
                'gh issue comment 670 --body-file C:body.md'
            )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_the_typed_write_is_classified_before_path_resolution(self) -> None:
        result = hook.extract(
            "printf text > body.md; gh issue comment 670 --body-file body.md"
        )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "written-before-publish")

    def test_every_refusal_reports_the_folder_and_reconstructed_path(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            missing = root / "missing.md"
            rooted = hook.handle(
                AnUnreadableBodyIsRefused.payload(
                    f'cd "{root}" && gh issue comment 670 '
                    '--body-file missing.md'
                )
            )["hookSpecificOutput"]
        unrooted = hook.handle(
            AnUnreadableBodyIsRefused.payload(
                "gh issue comment 670 --body-file missing.md"
            )
        )["hookSpecificOutput"]

        self.assertIn(f"resolved against: {root}", rooted["additionalContext"])
        self.assertIn(f"reconstructed path: {missing}", rooted["additionalContext"])
        self.assertIn("resolved against: none readable", unrooted["additionalContext"])
        self.assertIn("reconstructed path: missing.md", unrooted["additionalContext"])
        self.assertEqual(rooted["permissionDecision"], "deny")
        self.assertEqual(unrooted["permissionDecision"], "deny")

    def test_an_absolute_path_does_not_report_an_unrelated_cd(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            missing = root / "elsewhere" / "missing.md"
            response = hook.handle(
                AnUnreadableBodyIsRefused.payload(
                    f'cd "{root}" && gh issue comment 670 '
                    f'--body-file "{missing}"'
                )
            )["hookSpecificOutput"]["additionalContext"]

        self.assertIn("resolved against: none (path was absolute)", response)
        self.assertNotIn(f"resolved against: {root}", response)

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
    def test_a_verdict_without_a_discriminator_clause_is_advisory(self) -> None:
        result = hook.analyze(
            hook.Publication("body", "**Verdict:** HOLDS"),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

        self.assertIn(
            ("verdict:missing-discriminator", "advise"),
            [(row.rule, row.posture) for row in result.findings],
        )

    def test_a_three_space_markdown_verdict_is_still_a_verdict(self) -> None:
        result = hook.analyze(
            hook.Publication("body", "   **Verdict:** HOLDS"),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

        self.assertIn(
            "verdict:missing-discriminator",
            [row.rule for row in result.findings],
        )

    def test_an_invalid_backtick_opener_does_not_hide_a_live_verdict(self) -> None:
        result = hook.analyze(
            hook.Publication(
                "body", "```text ` is not a fence\n**Verdict:** HOLDS"
            ),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

        self.assertIn(
            "verdict:missing-discriminator",
            [row.rule for row in result.findings],
        )

    def test_a_nonparagraph_quote_does_not_hide_a_following_verdict(self) -> None:
        prefixes = (
            "> # Quoted heading\n",
            "> Quoted paragraph\n>\n",
        )
        for prefix in prefixes:
            with self.subTest(prefix=prefix):
                result = hook.analyze(
                    hook.Publication("body", prefix + "**Verdict:** HOLDS"),
                    index=phi_scan.build_index(set(), set()),
                    issue=None,
                    remote_fresh=True,
                )
                self.assertIn(
                    "verdict:missing-discriminator",
                    [row.rule for row in result.findings],
                )

    def test_a_verdict_after_a_fenced_list_example_stays_in_the_example(self) -> None:
        body = "- ```text\n  example\n  ```\n  **Verdict:** HOLDS"

        result = hook.analyze(
            hook.Publication("body", body),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

        self.assertNotIn(
            "verdict:missing-discriminator",
            [row.rule for row in result.findings],
        )

    def test_a_nested_block_ends_a_list_lazy_paragraph(self) -> None:
        nested_blocks = (
            "  # heading\n",
            "  > quote\n",
            "  - nested\n",
            "  ---\n",
        )
        for nested_block in nested_blocks:
            with self.subTest(nested_block=nested_block):
                result = hook.analyze(
                    hook.Publication(
                        "body",
                        "- Example:\n" + nested_block + "**Verdict:** HOLDS",
                    ),
                    index=phi_scan.build_index(set(), set()),
                    issue=None,
                    remote_fresh=True,
                )

                self.assertIn(
                    "verdict:missing-discriminator",
                    [row.rule for row in result.findings],
                )

    def test_an_html_block_ends_a_lazy_container_paragraph(self) -> None:
        html_blocks = (
            "<script>",
            "<!-- example",
            "<?example",
            "<!DOCTYPE html>",
            "<![CDATA[example",
            "<div>",
            "</div>",
        )
        containers = (
            lambda block: f"> {block}\n",
            lambda block: f"- Example:\n  {block}\n",
        )
        for html_block in html_blocks:
            for container in containers:
                with self.subTest(html_block=html_block, container=container):
                    result = hook.analyze(
                        hook.Publication(
                            "body",
                            container(html_block) + "**Verdict:** HOLDS",
                        ),
                        index=phi_scan.build_index(set(), set()),
                        issue=None,
                        remote_fresh=True,
                    )

                    self.assertIn(
                        "verdict:missing-discriminator",
                        [row.rule for row in result.findings],
                    )

    def test_html_block_contents_cannot_supply_the_discriminator(self) -> None:
        examples = (
            "<!--\nUnder the claim's negation this differs.\n-->",
            "> <!--\n> Under the claim's negation this differs.\n> -->",
            "- <!--\n  Under the claim's negation this differs.\n  -->",
        )
        for example in examples:
            with self.subTest(example=example):
                result = hook.analyze(
                    hook.Publication(
                        "body", "**Verdict:** HOLDS\n\n" + example
                    ),
                    index=phi_scan.build_index(set(), set()),
                    issue=None,
                    remote_fresh=True,
                )

                self.assertIn(
                    "verdict:missing-discriminator",
                    [row.rule for row in result.findings],
                )

    def test_html_block_contents_cannot_supply_a_live_verdict(self) -> None:
        blocks = (
            "<!--\n**Verdict:** HOLDS\n-->",
            "<script>\n**Verdict:** HOLDS\n</script>",
            "<div>\n**Verdict:** HOLDS\n\n",
            "> <!--\n> **Verdict:** HOLDS\n> -->",
            "- <!--\n  **Verdict:** HOLDS\n  -->",
        )
        for body in blocks:
            with self.subTest(body=body):
                result = hook.analyze(
                    hook.Publication("body", body),
                    index=phi_scan.build_index(set(), set()),
                    issue=None,
                    remote_fresh=True,
                )

                self.assertNotIn(
                    "verdict:missing-discriminator",
                    [row.rule for row in result.findings],
                )

    def test_a_type_one_html_block_uses_the_first_exact_family_closer(self) -> None:
        closed = hook.analyze(
            hook.Publication(
                "body", "<script>\n</style>\n**Verdict:** HOLDS"
            ),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )
        still_open = hook.analyze(
            hook.Publication(
                "body", "<script>\n</script   >\n**Verdict:** HOLDS"
            ),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

        self.assertIn(
            "verdict:missing-discriminator",
            [row.rule for row in closed.findings],
        )
        self.assertNotIn(
            "verdict:missing-discriminator",
            [row.rule for row in still_open.findings],
        )

    def test_the_discriminator_clause_clears_the_form_check(self) -> None:
        body = (
            "**Verdict:** HOLDS\n\n"
            "Under the claim's negation this instrument reports a different value."
        )
        result = hook.analyze(
            hook.Publication("body", body),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

        self.assertNotIn(
            "verdict:missing-discriminator",
            [row.rule for row in result.findings],
        )

    def test_an_example_only_discriminator_does_not_clear_a_live_verdict(self) -> None:
        examples = (
            "```text\nUnder the claim's negation this differs.\n```",
            "> Under the claim's negation this differs.",
            "- Under the claim's negation this differs.",
            "- Example:\n  Under the claim's negation this differs.",
        )
        for example in examples:
            with self.subTest(example=example):
                result = hook.analyze(
                    hook.Publication(
                        "body", "**Verdict:** HOLDS\n\n" + example
                    ),
                    index=phi_scan.build_index(set(), set()),
                    issue=None,
                    remote_fresh=True,
                )
                self.assertIn(
                    "verdict:missing-discriminator",
                    [row.rule for row in result.findings],
                )

    def test_the_verdict_form_check_is_comment_scoped(self) -> None:
        result = hook.analyze(
            hook.Publication("body", "**Verdict:** HOLDS"),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
            route=("issue", "edit"),
        )

        self.assertNotIn(
            "verdict:missing-discriminator",
            [row.rule for row in result.findings],
        )

    def test_an_issue_close_comment_is_checked(self) -> None:
        result = hook.analyze(
            hook.Publication("body", "**Verdict:** HOLDS"),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
            route=("issue", "close"),
        )

        self.assertIn(
            "verdict:missing-discriminator",
            [row.rule for row in result.findings],
        )

    def test_examples_of_verdicts_are_not_the_comments_verdict(self) -> None:
        examples = (
            "> **Verdict:** HOLDS",
            "- **Verdict:** HOLDS",
            "- Example:\n  **Verdict:** HOLDS",
            "    **Verdict:** HOLDS",
            "```text\n**Verdict:** HOLDS\n```",
        )
        for body in examples:
            with self.subTest(body=body):
                result = hook.analyze(
                    hook.Publication("body", body),
                    index=phi_scan.build_index(set(), set()),
                    issue=None,
                    remote_fresh=True,
                )
                self.assertNotIn(
                    "verdict:missing-discriminator",
                    [row.rule for row in result.findings],
                )

    def test_a_c0_control_character_denies_a_body_and_a_title(self) -> None:
        index = phi_scan.build_index(set(), set())

        for field in ("body", "title"):
            with self.subTest(field=field):
                result = hook.analyze(
                    hook.Publication(field, "damaged\btext"),
                    index=index,
                    issue=None,
                    remote_fresh=True,
                )
                controls = [
                    row for row in result.findings
                    if row.rule == "body:c0-control-character"
                ]
                self.assertEqual(
                    [(row.field, row.posture) for row in controls],
                    [(field, "deny")],
                )

    def test_escape_collapse_symptoms_deny_bodies(self) -> None:
        index = phi_scan.build_index(set(), set())
        cases = (
            ("before\rafter", "body:carriage-return-flanked"),
            (r"before\nafter", "body:literal-newline-escape"),
            (r"open D:\\folder", "body:doubled-path-separator"),
        )

        for body, rule in cases:
            with self.subTest(rule=rule):
                result = hook.analyze(
                    hook.Publication("body", body),
                    index=index,
                    issue=None,
                    remote_fresh=True,
                )
                self.assertIn(
                    (rule, "deny"),
                    [(row.rule, row.posture) for row in result.findings],
                )

    def test_title_exclusions_are_preserved(self) -> None:
        index = phi_scan.build_index(set(), set())

        for title in (r"before\nafter", r"open D:\\folder"):
            with self.subTest(title=title):
                result = hook.analyze(
                    hook.Publication("title", title),
                    index=index,
                    issue=None,
                    remote_fresh=True,
                )
                self.assertFalse(
                    any(row.rule.startswith("body:") for row in result.findings)
                )

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

    def test_a_failed_fetch_declares_unverified_positive_scope(self) -> None:
        body = (
            "> **Branch state:** this text rests on `main` at "
            "`abcdef0123456789abcdef0123456789abcdef01` as of `2026-09-03`.\n\n"
            "Merged behavior."
        )
        with mock.patch.object(
            hook.tracker_branch_scope, "_main_ancestry", return_value=False
        ) as ancestry:
            result = hook.analyze(
                hook.Publication("body", body),
                index=phi_scan.build_index(set(), set()),
                issue={"number": 737, "labels": ["in flight"]},
                remote_fresh=False,
            )

        ancestry.assert_called_once()
        self.assertEqual([], [row for row in result.findings if row.posture == "deny"])
        self.assertIn("positive Branch state accepted without ancestry verification", result.report)

    def test_a_failed_fetch_does_not_claim_an_unverified_positive_scope_without_one(self) -> None:
        result = hook.analyze(
            hook.Publication("body", "Ordinary tracker prose."),
            index=phi_scan.build_index(set(), set()),
            issue={"number": 737, "labels": []},
            remote_fresh=False,
        )

        self.assertNotIn(
            "positive Branch state accepted without ancestry verification",
            result.report,
        )

    def test_a_failed_tree_read_surfaces_the_not_graded_citation_row(self) -> None:
        with mock.patch.object(
            hook.tracker_branch_scope, "_default_branch_paths", return_value=None
        ):
            result = hook.analyze(
                hook.Publication(
                    "body",
                    "https://github.com/example/repo/blob/main/docs/missing.md",
                ),
                index=phi_scan.build_index(set(), set()),
                issue=None,
                remote_fresh=True,
            )

        self.assertIn("citation path resolution NOT GRADED", result.report)
        self.assertFalse(result.findings)

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
            specific = response["hookSpecificOutput"]
            report = specific["additionalContext"]
            self.assertIn("NOT SCANNED", report)
            self.assertNotIn("0 findings", report)
            self.assertEqual(specific["permissionDecision"], "deny")

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
                "fetch_readback",
                return_value=fetched_records(670),
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

    def test_a_missing_discriminator_is_reported_without_denying(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(670),
            ),
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body '**Verdict:** HOLDS'")
            )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn(
            "advise: verdict:missing-discriminator",
            specific["additionalContext"],
        )

    def test_a_pr_review_comment_crosses_the_same_advisory(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(706),
            ),
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload(
                    "gh pr review --comment 706 --body '**Verdict:** HOLDS'"
                )
            )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn(
            "advise: verdict:missing-discriminator",
            specific["additionalContext"],
        )

    def test_an_api_issue_edit_uses_issue_body_not_comment_rules(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(670),
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
                "fetch_readback",
                return_value=fetched_records(670, ("in flight",)),
            ):
                denied = hook.handle(
                    self.payload("gh issue comment 670 --body 'Ordinary body'")
                )
            with mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(670),
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

    def test_a_control_character_in_title_or_body_refuses_the_publication(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(723),
            ),
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload(
                    'gh issue edit 723 --title "damaged\btitle" '
                    '--body "damaged\bbody"'
                )
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("body:c0-control-character", specific["additionalContext"])
        self.assertNotIn("damaged", specific["additionalContext"])

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
        self.assertIn("analysis failed", crashed_report)
        self.assertEqual(
            crashed["hookSpecificOutput"]["permissionDecision"], "deny"
        )

    def test_an_exception_escaping_analyze_denies_the_publication(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback", return_value=fetched_records(670)),
            mock.patch.object(hook, "analyze", side_effect=RuntimeError("boom")),
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body 'Ordinary body'")
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("analysis failed (RuntimeError)", specific["additionalContext"])
        self.assertNotIn("Unreadable body", specific["additionalContext"])

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

    def test_title_and_body_share_one_batched_record_readback(self) -> None:
        index = phi_scan.build_index(set(), set())
        fetched = {
            17: {
                "number": 17,
                "state": "OPEN",
                "labels": {"nodes": []},
                "updatedAt": "2026-09-01T12:34:56Z",
                "body": "seventeen",
                "url": "https://github.com/example/project/issues/17",
            },
            18: None,
            670: {
                "number": 670,
                "state": "OPEN",
                "labels": {"nodes": []},
                "updatedAt": "2026-09-01T12:34:56Z",
                "body": "target",
                "url": "https://github.com/example/project/issues/670",
            },
        }
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback", return_value=fetched) as fetch,
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload(
                    "gh issue edit 670 --title 'Title cites #17' "
                    "--body 'Body cites #18 and #17'"
                )
            )

        fetch.assert_called_once_with(frozenset({17, 18, 670}))
        report = response["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(report.count("tracker readback: #17 "), 1)
        self.assertIn("tracker readback: #18 unresolved", report)
        self.assertIn("tracker readback: #670 state=OPEN", report)
        self.assertNotIn("seventeen", report)

    def test_a_text_bearing_create_with_no_citation_names_class_c(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback") as fetch,
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload(
                    "gh issue create --title 'A title' --body 'No record named'"
                )
            )

        fetch.assert_not_called()
        self.assertIn(
            "no cited record number; class (c) is reached by no mechanism",
            response["hookSpecificOutput"]["additionalContext"],
        )

    def test_a_failed_readback_degrades_context_blind_and_says_so(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback", side_effect=OSError("offline")),
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body 'Cites #17'")
            )

        report = response["hookSpecificOutput"]["additionalContext"]
        self.assertIn("tracker readback: FETCH FAILED; context-blind", report)
        self.assertIn("record number and labels were not read", report)

    def test_a_malformed_fetched_record_uses_the_same_context_blind_path(self) -> None:
        index = phi_scan.build_index(set(), set())
        malformed = fetched_records(670)
        del malformed[670]["updatedAt"]
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback", return_value=malformed),
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body 'Cites #17'")
            )

        report = response["hookSpecificOutput"]["additionalContext"]
        self.assertIn("tracker readback: FETCH FAILED; context-blind", report)
        self.assertIn("record number and labels were not read", report)
        self.assertNotIn("HOOK FAILURE", report)

    def test_a_target_record_without_a_url_is_context_blind(self) -> None:
        index = phi_scan.build_index(set(), set())
        malformed = fetched_records(670)
        del malformed[670]["url"]
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback", return_value=malformed),
            mock.patch.object(hook, "write_marker"),
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body 'Cites #17'")
            )

        report = response["hookSpecificOutput"]["additionalContext"]
        self.assertIn("tracker readback: FETCH FAILED; context-blind", report)
        self.assertNotIn("HOOK FAILURE", report)


class BatchedGraphqlReadback(unittest.TestCase):
    def test_a_nonzero_exit_with_a_payload_is_parsed(self) -> None:
        payload = {
            "data": {
                "repository": {
                    "record_17": {
                        "number": 17,
                        "state": "OPEN",
                        "labels": {"nodes": []},
                        "updatedAt": "2026-09-01T12:34:56Z",
                        "body": "record body",
                        "url": "https://github.com/example/project/issues/17",
                    },
                    "record_18": None,
                }
            },
            "errors": [{"message": "Could not resolve record 18"}],
        }
        completed = mock.Mock(returncode=1, stdout=json.dumps(payload), stderr="error")
        with mock.patch.object(hook.subprocess, "run", return_value=completed) as run:
            records = hook.fetch_readback(frozenset({17, 18}))

        self.assertEqual(records[17]["number"], 17)
        self.assertIsNone(records[18])
        self.assertNotIn("check", run.call_args.kwargs)
        command = run.call_args.args[0]
        self.assertEqual(command[:3], ["gh", "api", "graphql"])
        self.assertEqual(command.count("graphql"), 1)

    def test_an_omitted_alias_is_not_misreported_as_an_explicit_null(self) -> None:
        payload = {"data": {"repository": {}}}
        completed = mock.Mock(returncode=1, stdout=json.dumps(payload), stderr="error")
        with mock.patch.object(hook.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(ValueError, "omitted requested record"):
                hook.fetch_readback(frozenset({17}))


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


class DeclaredLimitsHaveOneOwner(unittest.TestCase):
    def test_the_ratified_population_is_present_in_both_directions(self):
        """Two rulings own this object, and each row belongs to exactly one.

        ADR 0089 ratified the four bypass rows -- ways the hook never runs at
        all. ADR 0096 added the three that describe what a run it *did* perform
        does not establish, and ADR 0104 adds the failed-readback path, on the
        rule this object already carried: a limit lives here rather than in the
        docstring or ``CLAUDE.md``. ADR 0109 adds the AAR paraphrase ceiling.
        """
        self.assertEqual(
            set(dict(hook.NOT_REACHED)),
            {
                "the GitHub web UI bypasses the hook",
                "disabled or overridden hooks bypass the check",
                "retained pre-edit revisions remain readable",
                "workspace trust can silently suppress registration",
                "a file rewritten after the scan is graded on its earlier text",
                "expansion is reconstructed and reaches only the same command",
                "the refusing hook covers one of two publishers",
                "a failed tracker readback leaves the publication context-blind",
                "an AAR paraphrase passes the quotation gate",
                "the command-folder reader reaches literal absolute cd targets only",
                "a stock discriminator clause can satisfy the verdict form check",
            },
        )



class AnUnreadableBodyIsRefused(unittest.TestCase):
    """#745. The gate returned *allow* whenever it could not read its input.

    The branch-scope limb is a refusal, so a gate that steps aside exactly when
    it cannot vouch for the text is not one. Every kind in
    ``UNREADABLE_REMEDIES`` denies, and the reason says the publication was not
    scanned rather than repeating the branch-scope sentence.
    """

    @staticmethod
    def payload(command: str) -> dict:
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }

    def test_an_unresolvable_variable_denies_and_names_the_reason(self) -> None:
        response = self.payload('gh issue comment 670 --body-file "$NOWHERE/b.md"')
        specific = hook.handle(response)["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertEqual(
            specific["permissionDecisionReason"], hook.UNSCANNED_REFUSAL
        )
        self.assertNotIn("branch-scope", specific["permissionDecisionReason"])

    def test_a_branch_scope_refusal_keeps_its_own_reason(self) -> None:
        """The reason became a parameter here; the other caller must not inherit."""
        response = hook._hook_response("deny", "report")

        self.assertEqual(
            response["hookSpecificOutput"]["permissionDecisionReason"],
            hook.BRANCH_SCOPE_REFUSAL,
        )

    def test_an_unrecognized_command_is_still_untouched(self) -> None:
        """The refusal is bounded by the publish routes and nothing wider."""
        self.assertEqual(hook.handle(self.payload("ls -la")), {})
        self.assertEqual(
            hook.handle(self.payload("gh issue view 670 --json body")), {}
        )


class ThePathFormsThatEscapedAreResolved(unittest.TestCase):
    """#745. The hook reads the command as typed, before the shell runs.

    There is no expanded argument to observe, so expansion is reconstructed
    from assignments in the same command. Only a value that was *entirely* one
    variable was substituted, so the ordinary ``$VAR/name.md`` form reached the
    filesystem check as an unexpanded literal, missed, and was reported as a
    missing file -- which was advisory, so the publication proceeded ungraded.
    """

    def setUp(self) -> None:
        self.directory = Path(tempfile.mkdtemp())
        self.body = self.directory / "body.md"
        self.body.write_text("recorded text\n", encoding="utf-8")
        self.windows = str(self.body).replace("\\", "/")

    def read(self, argument: str, prefix: str = "") -> hook.Extraction:
        return hook.extract(
            prefix + f"gh issue comment 670 --body-file {argument}"
        )

    def assertReadTheFile(self, got: hook.Extraction) -> None:
        self.assertEqual(got.unreadable, ())
        self.assertEqual(got.publications[0].text, "recorded text\n")

    def test_a_variable_naming_the_whole_path_still_resolves(self) -> None:
        self.assertReadTheFile(
            self.read('"$S"', prefix=f'S="{self.windows}"; ')
        )

    def test_a_variable_naming_a_path_prefix_resolves(self) -> None:
        self.assertReadTheFile(
            self.read(
                '"$S/body.md"', prefix=f'S="{self.directory.as_posix()}"; '
            )
        )

    def test_the_braced_spelling_resolves_too(self) -> None:
        self.assertReadTheFile(
            self.read(
                '"${S}/body.md"', prefix=f'S="{self.directory.as_posix()}"; '
            )
        )

    def test_a_literal_path_resolves(self) -> None:
        self.assertReadTheFile(self.read(f'"{self.windows}"'))

    @unittest.skipUnless(sys.platform == "win32", "MSYS spelling is Windows-only")
    def test_a_git_bash_path_resolves_in_its_windows_spelling(self) -> None:
        """MSYS rewrites this when it launches a native command, so the
        argument the shell used opens and the hook's earlier copy does not."""
        drive, rest = self.windows.split(":", 1)

        self.assertReadTheFile(self.read(f'"/{drive.lower()}{rest}"'))

    def test_a_variable_from_the_environment_is_classified_as_one(self) -> None:
        """It reported ``missing-file``, so the remedy printed was the wrong
        one -- create the file, for a path the hook could never have built."""
        got = self.read('"$NOWHERE/body.md"')

        self.assertEqual(got.unreadable[0].kind, "external-variable")

    def test_a_command_substitution_prefix_is_classified_as_one(self) -> None:
        got = self.read('"$D/body.md"', prefix='D="$(pwd)"; ')

        self.assertEqual(got.unreadable[0].kind, "command-substitution")

    def test_an_inline_body_expands_the_same_way(self) -> None:
        """``_expand`` serves the inline field too, where the value is the text
        rather than a path, so the two cannot drift apart."""
        got = hook.extract('S="text"; gh issue comment 670 --body "$S/tail"')

        self.assertEqual(got.publications[0].text, "text/tail")


class AnAarPublicationCannotQuoteItsRun(unittest.TestCase):
    def publication(self, copied: int, *, aar_owned: bool = True) -> hook.Publication:
        self.temporary = tempfile.TemporaryDirectory()
        run = Path(self.temporary.name) / "course-module-discussion"
        source = run / "post.md"
        source.parent.mkdir(parents=True)
        material = "A deliberately distinctive private working sentence " * 4
        source.write_text(material, encoding="utf-8")
        if aar_owned:
            body = run / "aar" / "publications" / "ticket.md"
        else:
            body = run / "ordinary-ticket.md"
        body.parent.mkdir(parents=True, exist_ok=True)
        text = material[:copied]
        body.write_text(text, encoding="utf-8")
        return hook.Publication("body", text, str(body))

    def tearDown(self) -> None:
        if hasattr(self, "temporary"):
            self.temporary.cleanup()

    def test_the_measured_floor_refuses_a_copied_span(self) -> None:
        publication = self.publication(hook.AAR_QUOTE_SPAN_CHARS)

        analysis = hook.aar_quotation_analysis((publication,))

        self.assertEqual([row.rule for row in analysis.findings], ["aar-quotation"])
        self.assertEqual(analysis.findings[0].posture, "deny")

    def test_one_character_below_the_floor_is_not_claimed(self) -> None:
        publication = self.publication(hook.AAR_QUOTE_SPAN_CHARS - 1)

        self.assertEqual(hook.aar_quotation_analysis((publication,)).findings, ())

    def test_an_ordinary_body_file_does_not_activate_the_aar_gate(self) -> None:
        publication = self.publication(hook.AAR_QUOTE_SPAN_CHARS + 20, aar_owned=False)

        self.assertEqual(hook.aar_quotation_analysis((publication,)).findings, ())

    def test_the_paraphrase_ceiling_is_declared(self) -> None:
        self.assertTrue(any("paraphrase" in subject for subject, _reason in hook.NOT_REACHED))


if __name__ == "__main__":
    unittest.main()
