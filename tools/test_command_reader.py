"""Tests for the command reader's public reading and limits boundaries.

phi-scan: synthetic

Every identifier-shaped value is invented; no test publishes tracker text.
"""

from __future__ import annotations

import unittest
import json
from pathlib import Path
import tempfile
import contextlib
import subprocess
import sys
import os

import artifact_lock_test_support  # noqa: F401
import command_reader as hook


@contextlib.contextmanager
def working_directory(path: str):
    """Temporarily enter ``path`` on interpreters before ``contextlib.chdir``."""

    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)



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
            "gh issue edit 670 --title 'A revised title' --body 'The revised body'"
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

    def test_a_plain_inline_variable_is_refused_before_scanning(self) -> None:
        result = hook.extract(
            "BODY='Expanded tracker text'; "
            'gh issue comment 670 --body "$BODY"'
        )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "expansion-exposed-inline")

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

    def test_same_command_api_comment_identifier_is_reconstructed(self) -> None:
        result = hook.extract(
            "CID=123; gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertEqual(result.grade_route, ("issue", "comment"))
        self.assertEqual(result.number, 123)
        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("body", "Comment edit")],
        )

    def test_api_identifier_expands_only_in_shell_active_quotes(self) -> None:
        literal = hook.extract(
            "CID=7; gh api 'repos/example/project/issues/comments/$CID' "
            "-f body='Comment edit'"
        )
        active = hook.extract(
            'CID=7; gh api "repos/example/project/issues/comments/$CID" '
            "-f body='Comment edit'"
        )

        self.assertEqual(
            literal.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )
        self.assertIsNone(literal.number)
        self.assertEqual(active.grade_route, ("issue", "comment"))
        self.assertEqual(active.number, 7)

    def test_composite_api_endpoint_reconstructs_record_number(self) -> None:
        result = hook.extract(
            "A=1; B=2; gh api -X POST "
            "repos/example/project/issues/comments/$A$B -f body='Comment'"
        )

        self.assertEqual(result.grade_route, ("issue", "comment"))
        self.assertEqual(result.number, 12)

    def test_unrelated_endpoint_expansion_keeps_literal_record_number(self) -> None:
        result = hook.extract(
            'gh api -X POST "repos/example/project/issues/7/comments?foo=$X" '
            "-f body='Comment'"
        )

        self.assertEqual(result.grade_route, ("issue", "comment"))
        self.assertEqual(result.number, 7)

    def test_unresolved_structural_endpoint_expansion_is_unclassified(self) -> None:
        result = hook.extract(
            'gh api -X POST "repos/$OWNER/project/issues/7/comments" '
            "-f body='Comment'"
        )

        self.assertIsNone(result.grade_route)
        self.assertIsNone(result.number)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-endpoint",
        )

    def test_later_api_comment_identifier_assignment_is_not_reconstructed(self) -> None:
        result = hook.extract(
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'; CID=123"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable, ())
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_api_command_prefix_assignment_is_not_reconstructed(self) -> None:
        result = hook.extract(
            "CID=123 gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable, ())
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_prior_command_local_api_assignment_is_not_reconstructed(self) -> None:
        result = hook.extract(
            "CID=123 echo setup; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_unset_api_identifier_assignment_is_not_reconstructed(self) -> None:
        result = hook.extract(
            "CID=123; command unset CID; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_conditional_api_identifier_assignment_is_not_reconstructed(self) -> None:
        result = hook.extract(
            "CID=7; false && CID=9; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_intervening_command_makes_api_assignment_unreconstructable(self) -> None:
        result = hook.extract(
            "CID=7; opaque_step; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_command_qualified_noops_make_api_state_unreconstructable(self) -> None:
        commands = (
            "CID=7; command :; ",
            "CID=7; command true; ",
        )

        for prefix in commands:
            with self.subTest(prefix=prefix):
                result = hook.extract(
                    prefix
                    + "gh api repos/example/project/issues/comments/$CID "
                    "-f body='Comment edit'"
                )
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-identifier",
                )

    def test_shadowable_noop_makes_api_assignment_unreconstructable(self) -> None:
        result = hook.extract(
            "CID=7; :; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_unresolved_api_identifier_assignment_is_not_reconstructed(self) -> None:
        for assignment in ("CID=$OTHER", "CID=${OTHER}"):
            with self.subTest(assignment=assignment):
                result = hook.extract(
                    assignment
                    + "; gh api repos/example/project/issues/comments/$CID "
                    "-f body='Comment edit'"
                )
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-identifier",
                )

    def test_known_api_identifier_assignment_chain_is_reconstructed(self) -> None:
        result = hook.extract(
            "OTHER=7; CID=$OTHER; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertEqual(result.grade_route, ("issue", "comment"))
        self.assertEqual(result.number, 7)

    def test_known_embedded_api_identifier_assignments_are_reconstructed(self) -> None:
        commands = (
            "OTHER=7; CID=${OTHER}8; ",
            "A=1; B=2; CID=$A$B; ",
        )

        for prefix, number in zip(commands, (78, 12), strict=True):
            with self.subTest(prefix=prefix):
                result = hook.extract(
                    prefix
                    + "gh api repos/example/project/issues/comments/$CID "
                    "-f body='Comment edit'"
                )
                self.assertEqual(result.grade_route, ("issue", "comment"))
                self.assertEqual(result.number, number)

    def test_empty_api_identifier_assignment_is_refused(self) -> None:
        result = hook.extract(
            "CID=; gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_unquoted_api_assignment_cannot_inject_publication_options(self) -> None:
        result = hook.extract(
            "ARGS='7 -f body=Injected'; "
            "gh api repos/example/project/issues/comments/$ARGS"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable, ())
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-arguments",
        )

    def test_empty_quote_prefix_cannot_hide_an_injected_api_option(self) -> None:
        commands = (
            "ARGS=-f; gh api -X POST repos/example/project/issues/7/comments "
            "''$ARGS body=Injected",
            "ARGS=--method=POST; gh api -X GET "
            "repos/example/project/issues/7 -f body=x ''$ARGS",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.publications, ())
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

    def test_adjacent_variable_cannot_hide_an_injected_api_option(self) -> None:
        commands = (
            "A=7; B=' -f body=Injected'; "
            "gh api repos/example/project/issues/comments/$A$B",
            "A=7; B=' --method=POST'; gh api -X GET "
            "repos/example/project/issues/$A $B -f body=Injected",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.publications, ())
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

    def test_split_delimiter_and_option_variables_are_analyzed_together(self) -> None:
        result = hook.extract(
            "ID=7; SEP=' '; OPT='-X POST'; gh api -X GET "
            "repos/example/project/issues/$ID$SEP$OPT -f body=Injected"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-arguments",
        )

    def test_expansion_split_cannot_hide_a_literal_option_suffix(self) -> None:
        commands = (
            "SEP=' '; gh api -X GET "
            "repos/example/project/issues/7$SEP-X POST -f body=Injected",
            "SEP=' '; gh api -X GET "
            'repos/example/project/issues/7$SEP"-X" POST -f body=Injected',
            "SEP=' '; gh api -X GET "
            "repos/example/project/issues/7$SEP\\-X POST -f body=Injected",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

    def test_expansion_split_cannot_hide_a_quoted_variable_option(self) -> None:
        commands = (
            "SEP=' '; OPT='--method=POST'; gh api -X GET "
            'repos/o/r/issues/7 -f data=x$SEP"$OPT" -f body=Injected',
            "SEP=' '; OPT='-X'; gh api -X GET "
            'repos/o/r/issues/7 -f data=x$SEP"$OPT" POST -f body=Injected',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

        literal = hook.extract(
            "SEP=' '; OPT='--method=POST'; gh api -X GET "
            "repos/o/r/issues/7 -f data=x$SEP'$OPT'"
        )
        self.assertEqual(literal.unclassified_api_calls, ())

    def test_api_field_assignments_are_expanded_before_classification(self) -> None:
        commands = (
            "FIELD='body=Injected'; gh api "
            'repos/example/project/issues/comments/7 -f "$FIELD"',
            "FIELD='body=Injected'; gh api "
            "repos/example/project/issues/comments/7 -f $FIELD",
            "KEY=body; gh api repos/example/project/issues/comments/7 "
            '-f "$KEY=Injected"',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(result.grade_route, ("issue", "comment"))
                self.assertEqual(result.number, 7)
                self.assertEqual(result.publications[0].field, "body")
                self.assertEqual(result.publications[0].text, "Injected")

    def test_unknown_api_field_assignment_is_refused(self) -> None:
        result = hook.extract(
            'gh api repos/example/project/issues/comments/7 -f "$FIELD"'
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-arguments",
        )

    def test_known_api_field_with_unknown_value_is_unreadable(self) -> None:
        commands = (
            'gh api repos/o/r/issues/comments/7 -f "body=$VALUE"',
            'KEY=body; gh api repos/o/r/issues/comments/7 -f "$KEY=$VALUE"',
            'gh api repos/o/r/issues/7 -f "title=$VALUE"',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(result.unclassified_api_calls, ())
                self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_unknown_whole_api_option_is_refused(self) -> None:
        commands = (
            'gh api -X GET repos/o/r/issues/7 -f body=Injected "$OPT" POST',
            'gh api -X GET repos/o/r/issues/7 -f body=Injected "$OPT=POST"',
            'gh api -X GET "$OPT" POST repos/o/r/issues/7 -f body=Injected',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

    def test_unquoted_api_brace_expansion_is_refused(self) -> None:
        commands = (
            "gh api -X POST repos/o/r/issues/7/comments "
            "-fbody={Safe,Injected}",
            "gh api -X POST repos/o/r/issues/7/comments "
            "--raw-field=body={Safe,Injected}",
            "gh api -X POST repos/o/r/issues/7/comments "
            "-fbody='$'{Safe,Injected}",
            "gh api -X POST repos/o/r/issues/7/comments "
            "-fbody=\\${Safe,Injected}",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

        safe_commands = (
            "gh api -X POST repos/o/r/issues/7/comments "
            "-f'body={Safe,Injected}'",
            "gh api -X POST repos/o/r/issues/7/comments "
            "-fbody=\\{Safe,Injected\\}",
        )
        for command in safe_commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(result.grade_route, ("issue", "comment"))
                self.assertEqual(result.publications[0].text, "{Safe,Injected}")

        wholly_quoted = hook.extract(
            "gh api -X POST repos/o/r/issues/7/comments "
            "-fbody='${Safe,Injected}'"
        )
        self.assertEqual(wholly_quoted.grade_route, ("issue", "comment"))
        self.assertEqual(
            wholly_quoted.publications[0].text,
            "${Safe,Injected}",
        )

    def test_unquoted_api_pathname_expansion_is_refused(self) -> None:
        commands = (
            "gh api -X POST repos/o/r/issues/7/comments -f body=*",
            "gh api -X POST repos/o/r/issues/7/comments -f body=?",
            "gh api -X POST repos/o/r/issues/7/comments -f 'body=x'[ab]",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

        safe_commands = (
            "gh api -X POST repos/o/r/issues/7/comments -f 'body=*'",
            "gh api -X POST repos/o/r/issues/7/comments -f body=\\?",
            "gh api -X POST repos/o/r/issues/7/comments -f 'body=[ab]'",
        )
        for command in safe_commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(result.grade_route, ("issue", "comment"))

    def test_unquoted_api_process_substitution_is_refused(self) -> None:
        commands = (
            "gh api -X POST repos/o/r/issues/7/comments -f body=<(true)",
            "gh api -X POST repos/o/r/issues/7/comments -fbody=>(true)",
            "gh api -X POST repos/o/r/issues/7/comments "
            "-f body=<(printf Injected)",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

        safe_commands = (
            "gh api -X POST repos/o/r/issues/7/comments -f 'body=<(true)'",
            "gh api -X POST repos/o/r/issues/7/comments -f body=\\<(true)",
        )
        for command in safe_commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(result.grade_route, ("issue", "comment"))
                self.assertEqual(result.publications[0].text, "<(true)")

    def test_dynamic_attached_api_flag_preserves_value_quotes(self) -> None:
        commands = (
            "OPT=-f; gh api repos/o/r/issues/comments/7 "
            '"$OPT"\'body=$VALUE\'',
            "OPT=--raw-field=; gh api repos/o/r/issues/comments/7 "
            '"$OPT"\'body=$VALUE\'',
            "OPT=-f; gh api repos/o/r/issues/comments/7 "
            '"$OPT"body=\\$VALUE',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(result.grade_route, ("issue", "comment"))
                self.assertEqual(result.unreadable, ())
                self.assertEqual(result.publications[0].text, "$VALUE")

        graphql = hook.extract(
            "OPT=-f; gh api graphql "
            '"$OPT"\'query=query($owner:String!){viewer{login}}\''
        )
        self.assertEqual(graphql.unreadable, ())
        self.assertEqual(graphql.unclassified_api_calls, ())

    def test_unquoted_leading_tilde_api_argument_is_refused(self) -> None:
        commands = (
            "gh api graphql --input ~/body.json",
            "gh api -X POST repos/o/r/issues/7/comments -f body=~",
            "gh api -X POST repos/o/r/issues/7/comments -f body=x:~",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

        safe_commands = (
            "gh api -X POST repos/o/r/issues/7/comments -f 'body=~'",
            "gh api -X POST repos/o/r/issues/7/comments -fbody=~",
            "gh api -X POST repos/o/r/issues/7/comments -f 'body'=~",
            "gh api -X POST repos/o/r/issues/7/comments -f b'ody'=~",
            "gh api -X POST repos/o/r/issues/7/comments -f body\\=~",
        )
        for command in safe_commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(result.grade_route, ("issue", "comment"))
                self.assertEqual(result.publications[0].text, "~")

        later_equals = (
            ("body==~", "=~"),
            ("body=x=~", "x=~"),
        )
        for field, expected in later_equals:
            with self.subTest(field=field):
                result = hook.extract(
                    "gh api -X POST repos/o/r/issues/7/comments -f " + field
                )
                self.assertEqual(result.grade_route, ("issue", "comment"))
                self.assertEqual(result.publications[0].text, expected)

    def test_nondefault_ifs_cannot_inject_api_publication_options(self) -> None:
        commands = (
            "IFS=,; ARGS='7,-f,body=Injected'; ",
            "opaque_step; ARGS='7,-f,body=Injected'; ",
        )

        for prefix in commands:
            with self.subTest(prefix=prefix):
                result = hook.extract(
                    prefix
                    + "gh api repos/example/project/issues/comments/$ARGS"
                )
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.publications, ())
                self.assertEqual(result.unreadable, ())
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

    def test_double_quoted_api_identifier_assignment_chain_is_reconstructed(self) -> None:
        result = hook.extract(
            "OTHER=7; CID=\"$OTHER\"; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertEqual(result.grade_route, ("issue", "comment"))
        self.assertEqual(result.number, 7)

    def test_single_quoted_api_identifier_indirection_is_refused(self) -> None:
        result = hook.extract(
            "OTHER=7; CID='$OTHER'; "
            "gh api repos/example/project/issues/comments/$CID "
            "-f body='Comment edit'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-identifier",
        )

    def test_compound_api_identifier_assignment_is_refused(self) -> None:
        assignments = (
            "CID='1'${OTHER}'2'",
            "CID='7'8",
            'OTHER=7; CID="$OTHER"8',
        )

        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = hook.extract(
                    assignment
                    + "; gh api repos/example/project/issues/comments/$CID "
                    "-f body='Comment edit'"
                )
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-identifier",
                )

    def test_escape_bearing_api_identifier_assignment_is_refused(self) -> None:
        assignments = (
            "CID=7\\8",
            'CID="7\\\n8"',
        )

        for assignment in assignments:
            with self.subTest(assignment=assignment):
                result = hook.extract(
                    assignment
                    + "; gh api repos/example/project/issues/comments/$CID "
                    "-f body='Comment edit'"
                )
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-identifier",
                )

    def test_export_assignment_commands_make_api_state_unreconstructable(self) -> None:
        commands = (
            "command export OTHER=7 CID=$OTHER; ",
            "OTHER=9; command export OTHER=7 CID=$OTHER; ",
            "command export OTHER=7; command export CID=$OTHER; ",
        )

        for prefix in commands:
            with self.subTest(prefix=prefix):
                result = hook.extract(
                    prefix
                    + "gh api repos/example/project/issues/comments/$CID "
                    "-f body='Comment edit'"
                )
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-identifier",
                )

    def test_shadowable_assignment_builtins_invalidate_api_state(self) -> None:
        commands = (
            "CID=7; export OTHER=1; ",
            "CID=7; unset OTHER; ",
        )

        for prefix in commands:
            with self.subTest(prefix=prefix):
                result = hook.extract(
                    prefix
                    + "gh api repos/example/project/issues/comments/$CID "
                    "-f body='Comment edit'"
                )
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-identifier",
                )

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

    def test_markdown_render_fields_are_not_tracker_publications(self) -> None:
        result = hook.extract(
            "gh api markdown -f text='Text sent only to the renderer'"
        )

        self.assertEqual(result.route, ("api",))
        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable, ())

    def test_markdown_pipe_input_is_not_read_as_a_tracker_body(self) -> None:
        result = hook.extract("printf '%s' text | gh api markdown --input -")

        self.assertEqual(result.route, ("api",))
        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable, ())

    def test_named_text_free_api_writes_are_not_tracker_publications(self) -> None:
        commands = (
            "gh api repos/example/project/git/refs -f ref=refs/heads/topic",
            "gh api --method DELETE repos/example/project/git/refs/heads/topic",
            "gh api repos/example/project/issues/670/dependencies/blocked_by "
            "-f issue_id=671",
            "gh api --method DELETE "
            "repos/example/project/issues/670/dependencies/blocked_by/671",
            "gh api --method DELETE repos/example/project/issues/670/sub_issue",
            "gh api --method DELETE repos/example/project/issues/670/labels/bug",
            "gh api --method DELETE "
            "repos/example/project/issues/670/reactions/55",
            "gh api --method DELETE "
            "repos/example/project/issues/comments/777/reactions/55",
            "gh api --method DELETE "
            "repos/example/project/pulls/comments/888/reactions/55",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.publications, ())
                self.assertEqual(result.unreadable, ())

    def test_graphql_query_documents_are_read_only(self) -> None:
        commands = (
            "gh api graphql -f query='query { viewer { login } }'",
            "gh api graphql -f query='{ viewer { login } }'",
            "gh api graphql --raw-field=query='query { viewer { login } }'",
            "gh api graphql -fquery='query { viewer { login } }'",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.publications, ())
                self.assertEqual(result.unreadable, ())

    def test_graphql_query_operation_is_read_from_a_field_file(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "query.graphql").write_text(
                "query { viewer { login } }", encoding="utf-8"
            )
            command = (
                f'cd "{root.as_posix()}" && '
                "gh api graphql -F query=@query.graphql"
            )

            result = hook.extract(command)

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable, ())

    def test_graphql_field_file_expands_only_shell_active_path_variables(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "$FILE").write_text(
                "query { viewer { login } }", encoding="utf-8"
            )
            (root / "mutation.graphql").write_text(
                "mutation { deleteProjectV2(input: {}) { clientMutationId } }",
                encoding="utf-8",
            )
            prefix = f'cd "{root.as_posix()}"; FILE=mutation.graphql; '
            literal = hook.extract(
                prefix + "gh api graphql -F 'query=@$FILE'"
            )
            active = hook.extract(
                prefix + 'gh api graphql -F "query=@$FILE"'
            )

        self.assertIsNone(literal.grade_route)
        self.assertEqual(literal.unclassified_api_calls, ())
        self.assertEqual(
            active.unclassified_api_calls[0].kind,
            "unclassified-api-mutation",
        )

    def test_named_nonpublication_expansions_are_left_alone(self) -> None:
        commands = (
            "TEXT='hello world'; gh api markdown -f text=$TEXT",
            "REF='refs/heads/a b'; gh api repos/example/project/git/refs "
            "-f ref=$REF",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.publications, ())
                self.assertEqual(result.unreadable, ())
                self.assertEqual(result.unclassified_api_calls, ())

    def test_explicit_get_expansions_are_left_alone(self) -> None:
        result = hook.extract(
            "ARGS='body=hello world'; gh api -X GET "
            "repos/example/project/issues -f data=$ARGS"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable, ())
        self.assertEqual(result.unclassified_api_calls, ())

    def test_quoted_dash_text_does_not_become_an_injected_option(self) -> None:
        commands = (
            'A=text; gh api markdown -f note=$A" -safe"',
            'A=value; gh api -X GET repos/o/r/issues/7 '
            '-f data=$A" -safe"',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unclassified_api_calls, ())

    def test_dynamic_arguments_cannot_override_an_explicit_get(self) -> None:
        commands = (
            "ARGS='7 -X POST -f body=Injected'; gh api -X GET "
            "repos/example/project/issues/comments/$ARGS",
            "ARGS='--method=POST'; gh api -X GET "
            "repos/example/project/issues/7 -f body=x $ARGS",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

    def test_dynamic_owner_cannot_reshape_a_nonpublication_endpoint(self) -> None:
        result = hook.extract(
            "OWNER='example/project/issues/7/comments -f body=Injected'; "
            "gh api repos/$OWNER/x/issues/8/labels"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-arguments",
        )

    def test_graphql_query_operation_is_read_from_json_input(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "request.json").write_text(
                json.dumps({"query": "query { viewer { login } }"}),
                encoding="utf-8",
            )
            command = (
                f'cd "{root.as_posix()}" && '
                "gh api graphql --input request.json"
            )

            result = hook.extract(command)

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable, ())
        self.assertEqual(result.unclassified_api_calls, ())

    def test_graphql_input_expands_only_shell_active_path_variables(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "$FILE").write_text(
                json.dumps({"query": "query { viewer { login } }"}),
                encoding="utf-8",
            )
            (root / "mutation.json").write_text(
                json.dumps(
                    {
                        "query": (
                            "mutation { deleteProjectV2(input: {}) "
                            "{ clientMutationId } }"
                        )
                    }
                ),
                encoding="utf-8",
            )
            prefix = f'cd "{root.as_posix()}"; FILE=mutation.json; '
            literal = hook.extract(
                prefix + "gh api graphql --input '$FILE'"
            )
            active = hook.extract(
                prefix + 'gh api graphql --input "$FILE"'
            )

        self.assertIsNone(literal.grade_route)
        self.assertEqual(literal.unclassified_api_calls, ())
        self.assertEqual(
            active.unclassified_api_calls[0].kind,
            "unclassified-api-mutation",
        )

    def test_unreadable_graphql_query_file_is_refused_as_an_unreadable_body(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            command = (
                f'cd "{Path(folder).as_posix()}" && '
                "gh api graphql -F query=@missing.graphql"
            )

            result = hook.extract(command)

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "missing-file")

    def test_runtime_graphql_document_is_refused_as_an_unreadable_body(self) -> None:
        result = hook.extract('gh api graphql -f "query=$QUERY"')

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_later_graphql_assignment_does_not_make_the_document_readable(self) -> None:
        result = hook.extract(
            'gh api graphql -f "query=$QUERY"; '
            "QUERY='query { viewer { login } }'"
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_prior_command_local_graphql_assignment_is_not_reconstructed(self) -> None:
        result = hook.extract(
            "QUERY='query { viewer { login } }' echo setup; "
            'gh api graphql -f "query=$QUERY"'
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_unresolved_graphql_assignment_chain_is_refused(self) -> None:
        result = hook.extract(
            'QUERY=$OTHER; gh api graphql -f "query=$QUERY"'
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_reconstructed_graphql_endpoint_preserves_unreadable_remedy(self) -> None:
        commands = (
            'END=graphql; gh api "$END" -f "query=$QUERY"',
            'BASE=graph; END=${BASE}ql; gh api "$END" '
            '-f "operationName=$OPERATION" -f "query=$QUERY"',
            'END=graphql; KEY=query; gh api "$END" -f "$KEY=$QUERY"',
            'END=graphql; gh api "$END" --input "$REQUEST"',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unclassified_api_calls, ())
                self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_reconstructed_nonpublication_endpoint_keeps_read_bypass(self) -> None:
        commands = (
            "END=markdown; TEXT='hello world'; "
            'gh api "$END" -f text=$TEXT',
            "BASE=mark; END=${BASE}down; TEXT='hello world'; "
            'gh api "$END" -f text=$TEXT',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unclassified_api_calls, ())
                self.assertEqual(result.unreadable, ())

    def test_read_bypasses_allow_unknown_quoted_option_values(self) -> None:
        commands = (
            'gh api markdown -f "text=$TEXT"',
            'gh api -X GET repos/o/r/issues/7 -f "data=$VALUE"',
            'gh api -X PATCH repos/o/r/git/refs/heads/topic -f "ref=$REF"',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unclassified_api_calls, ())
                self.assertEqual(result.unreadable, ())

    def test_named_nonpublication_ignores_unknown_post_endpoint_words(self) -> None:
        commands = (
            'gh api markdown "$OPT" POST',
            "gh api markdown $OPT POST",
            'gh api repos/o/r/git/refs "$OPT" POST',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unclassified_api_calls, ())
                self.assertEqual(result.unreadable, ())

    def test_unquoted_graphql_assignment_cannot_inject_fields(self) -> None:
        commands = (
            "QUERY='query Q{viewer{login}} -f "
            "query=mutation{addComment(input:{body:Injected})"
            "{clientMutationId}}'; gh api graphql -f query=$QUERY",
            "TAIL='-f query=query{viewer{login}}'; gh api graphql "
            "-f query='mutation{deleteProjectV2(input:{})"
            "{clientMutationId}}' $TAIL",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.publications, ())
                self.assertEqual(result.unreadable, ())
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-arguments",
                )

    def test_single_quoted_graphql_variable_is_document_text(self) -> None:
        result = hook.extract(
            "QUERY='query($owner:String!){repository(owner:$owner){name}}'; "
            'gh api graphql -f "query=$QUERY"'
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable, ())
        self.assertEqual(result.unclassified_api_calls, ())

    def test_single_quoted_graphql_field_does_not_expand_shell_variable(self) -> None:
        commands = (
            "QUERY='mutation { x }'; gh api graphql -f 'query=$QUERY'",
            'QUERY="mutation { x }"; gh api graphql -f "query=\\$QUERY"',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unreadable, ())
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-endpoint",
                )

    def test_segmented_graphql_fields_expand_only_active_variables(self) -> None:
        commands = (
            "OP=mutation; gh api graphql -f query=''$OP' M{x}'",
            'OP=mutation; gh api graphql -f "query=${OP} M{x}"',
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unreadable, ())
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-mutation",
                )

    def test_known_embedded_graphql_assignment_is_reconstructed(self) -> None:
        result = hook.extract(
            "HEAD='query {'; TAIL='viewer { login }}'; QUERY=$HEAD$TAIL; "
            'gh api graphql -f "query=$QUERY"'
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable, ())
        self.assertEqual(result.unclassified_api_calls, ())

    def test_single_quoted_graphql_mutation_variable_gets_mutation_remedy(self) -> None:
        result = hook.extract(
            "QUERY='mutation($body:String!){addComment(input:{body:$body})"
            "{clientMutationId}}'; gh api graphql -f \"query=$QUERY\""
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable, ())
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-mutation",
        )

    def test_compound_graphql_assignment_is_refused(self) -> None:
        result = hook.extract(
            "QUERY='query { viewer { login } }'${TAIL}''; "
            'gh api graphql -f "query=$QUERY"'
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_unresolved_graphql_input_path_assignment_is_refused(self) -> None:
        result = hook.extract(
            'REQUEST=$OTHER; gh api graphql --input "$REQUEST"'
        )

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable[0].kind, "external-variable")

    def test_api_output_options_before_endpoint_do_not_change_its_route(self) -> None:
        commands = (
            "gh api --header Accept:application/json --method DELETE "
            "repos/example/project/git/refs/heads/topic",
            "gh api --jq . --method DELETE "
            "repos/example/project/git/refs/heads/topic",
            "gh api --template '{{.name}}' --method DELETE "
            "repos/example/project/git/refs/heads/topic",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertIsNone(result.grade_route)
                self.assertEqual(result.unreadable, ())

    def test_header_before_issue_endpoint_stays_on_the_issue_edit_route(self) -> None:
        result = hook.extract(
            "gh api --header Accept:application/json --method PATCH "
            "repos/example/project/issues/670 -f body='Issue edit'"
        )

        self.assertEqual(result.grade_route, ("issue", "edit"))
        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("body", "Issue edit")],
        )

    def test_attached_api_body_field_is_extracted(self) -> None:
        result = hook.extract(
            "gh api repos/example/project/issues/670 -fbody='Issue edit'"
        )

        self.assertEqual(result.grade_route, ("issue", "edit"))
        self.assertEqual(
            [(row.field, row.text) for row in result.publications],
            [("body", "Issue edit")],
        )

    def test_non_repository_issue_collection_is_unclassified(self) -> None:
        result = hook.extract("gh api orgs/example/issues -f body='Unknown route'")

        self.assertIsNone(result.grade_route)
        self.assertEqual(result.unreadable, ())
        self.assertEqual(
            result.unclassified_api_calls[0].kind,
            "unclassified-api-endpoint",
        )

    def test_every_named_api_publication_route_stays_classified(self) -> None:
        commands = (
            (("issue", "create"), "gh api repos/example/project/issues -f title='T'"),
            (("issue", "edit"), "gh api repos/example/project/issues/12 -f body='B'"),
            (("issue", "comment"), (
                "gh api repos/example/project/issues/12/comments -f body='B'"
            )),
            (("issue", "comment"), (
                "gh api repos/example/project/issues/comments/12 -f body='B'"
            )),
            (("pr", "create"), "gh api repos/example/project/pulls -f title='T'"),
            (("pr", "edit"), "gh api repos/example/project/pulls/13 -f body='B'"),
            (("pr", "comment"), (
                "gh api repos/example/project/pulls/13/comments -f body='B'"
            )),
            (("pr", "comment"), (
                "gh api repos/example/project/pulls/comments/13 -f body='B'"
            )),
            (("pr", "review"), (
                "gh api repos/example/project/pulls/13/reviews -f body='B'"
            )),
        )

        for expected, command in commands:
            with self.subTest(route=expected):
                result = hook.extract(command)
                self.assertEqual(result.grade_route, expected)
                self.assertTrue(result.publications)

    def test_api_field_files_expand_only_shell_active_path_variables(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "$FILE").write_text("Literal body", encoding="utf-8")
            (root / "safe.md").write_text("Active body", encoding="utf-8")
            prefix = f'cd "{root.as_posix()}"; FILE=safe.md; '
            commands = (
                (
                    prefix
                    + "gh api repos/o/r/issues/comments/7 -F 'body=@$FILE'",
                    "Literal body",
                ),
                (
                    prefix
                    + 'gh api repos/o/r/issues/comments/7 -F "body=@$FILE"',
                    "Active body",
                ),
                (
                    prefix
                    + 'gh api repos/o/r/issues/comments/7 -F "body=@\\$FILE"',
                    "Literal body",
                ),
            )

            for command, expected in commands:
                with self.subTest(command=command):
                    result = hook.extract(command)
                    self.assertEqual(result.grade_route, ("issue", "comment"))
                    self.assertEqual(result.publications[0].text, expected)

    def test_composite_api_identifiers_keep_identifier_remedy(self) -> None:
        commands = (
            "gh api repos/o/r/issues/comments/${IDS[$n]} -f body=x",
            "A=1; gh api repos/o/r/issues/comments/$A$B -f body=x",
        )

        for command in commands:
            with self.subTest(command=command):
                result = hook.extract(command)
                self.assertEqual(
                    result.unclassified_api_calls[0].kind,
                    "unclassified-api-identifier",
                )


class InlineTrackerTextMustBeShellReproducible(unittest.TestCase):
    @staticmethod
    def shell_value(value: str, *, variables: dict[str, str] | None = None) -> str:
        command = f"printf '%s' {value}"
        environment = os.environ.copy()
        environment.update(variables or {})
        git_bash = Path("C:/Program Files/Git/bin/bash.exe")
        executable = str(git_bash) if git_bash.is_file() else "bash"
        return subprocess.run(
            [executable, "-c", command],
            text=True,
            encoding="utf-8",
            errors="strict",
            capture_output=True,
            check=True,
            env=environment,
        ).stdout

    def test_an_escaped_apostrophe_splice_matches_the_real_shell(self) -> None:
        value = r"'it'\''s'"

        result = hook.extract(f"gh issue comment 670 --body {value}")

        self.assertEqual(result.unreadable, ())
        self.assertEqual(result.publications[0].text, self.shell_value(value))

    def test_outside_quote_escaped_separators_match_the_real_shell(self) -> None:
        for value in (r"'a'\|'b'", r"'a'\;'b'", r"'a'\&'b'", "'a'\\\n'b'"):
            with self.subTest(value=value):
                result = hook.extract(f"gh issue comment 670 --body {value}")

                self.assertEqual(result.unreadable, ())
                self.assertEqual(result.publications[0].text, self.shell_value(value))

    def test_one_expansion_exposed_segment_refuses_the_whole_value(self) -> None:
        value = "'a'\"$T\"'c'"
        shell_text = self.shell_value(value, variables={"T": "set"})

        result = hook.extract(f"T=set; gh issue comment 670 --body {value}")

        self.assertEqual(shell_text, "asetc")
        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "expansion-exposed-inline")

    def test_a_wholly_single_quoted_api_field_is_reproducible(self) -> None:
        result = hook.extract(
            "gh api repos/example/project/issues/670/comments "
            "-f 'body=API comment'"
        )

        self.assertEqual(result.unreadable, ())
        self.assertEqual(result.publications[0].text, "API comment")

    def test_a_wholly_single_quoted_attached_flag_is_reproducible(self) -> None:
        for command in (
            "gh issue comment 670 '--body=Attached body'",
            "gh issue close 670 '--comment=Closing body'",
        ):
            with self.subTest(command=command):
                result = hook.extract(command)

                self.assertEqual(result.unreadable, ())
                self.assertEqual(len(result.publications), 1)

    def test_an_unspaced_redirection_is_not_part_of_the_inline_value(self) -> None:
        for command, field in (
            ("gh issue comment 670 --body 'clean'>out", "body"),
            ("gh issue comment 670 '--body=clean'>out", "body"),
            ("gh issue edit 670 --title 'clean'>out", "title"),
        ):
            with self.subTest(command=command):
                result = hook.extract(command)

                self.assertEqual(result.unreadable, ())
                self.assertEqual(
                    [(row.field, row.text) for row in result.publications],
                    [(field, "clean")],
                )


class FileBackedTrackerTextIsRead(unittest.TestCase):
    def test_a_literal_body_file_is_read_and_named(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "issue.md"
            body.write_text("File-backed body", encoding="utf-8")

            result = hook.extract(f'gh issue comment 670 --body-file "{body}"')

        self.assertEqual(
            [(row.field, row.text, row.origin, row.path) for row in result.publications],
            [("body", "File-backed body", "body-file", body.resolve())],
        )
        self.assertEqual(result.unreadable, ())

    def test_a_partial_body_file_uses_the_literal_cd_not_the_hook_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as command_directory:
            root = Path(command_directory)
            body = root / "scratch" / "body.md"
            body.parent.mkdir()
            body.write_text("Command-rooted body", encoding="utf-8")
            with tempfile.TemporaryDirectory() as hook_directory:
                with working_directory(hook_directory):
                    result = hook.extract(
                        f'cd "{root}" && gh issue comment 670 '
                        '--body-file scratch/body.md'
                    )

        self.assertEqual(
            [(row.field, row.text, row.origin, row.path) for row in result.publications],
            [("body", "Command-rooted body", "body-file", body.resolve())],
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
        self.assertEqual(result.publications[0].path, body.resolve())

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
                with working_directory(hook_directory):
                    result = hook.extract(
                        f'cd "{root}" && gh api repos/example/project/issues/670 '
                        '--input request.json'
                    )

        self.assertEqual(
            [(row.field, row.text, row.origin, row.path) for row in result.publications],
            [("body", "Rooted input body", "body-file", document.resolve())],
        )

    def test_api_json_can_arrive_in_an_inline_heredoc(self) -> None:
        command = (
            "gh api repos/example/project/issues/670 --input - <<'JSON'\n"
            '{"body": "Heredoc API body"}\n'
            "JSON\n"
        )

        result = hook.extract(command)

        self.assertEqual(
            [(row.field, row.text, row.origin) for row in result.publications],
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
            with working_directory(hook_directory):
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

    def test_an_unrooted_path_is_classified_before_file_absence(self) -> None:
        result = hook.extract(
            "printf text > body.md; gh issue comment 670 --body-file body.md"
        )

        self.assertEqual(result.publications, ())
        self.assertEqual(result.unreadable[0].kind, "unrooted-path")

    def test_an_inline_heredoc_is_read_from_the_command(self) -> None:
        command = (
            "gh issue create --title 'Ticket' --body-file - <<'BODY'\n"
            "First line\nSecond line\n"
            "BODY\n"
        )

        result = hook.extract(command)

        self.assertEqual(
            [(row.field, row.text, row.origin) for row in result.publications],
            [
                ("title", "Ticket", "inline"),
                ("body", "First line\nSecond line", "inline heredoc"),
            ],
        )
        self.assertEqual(result.unreadable, ())


class ProjectSettingsRegisterTheHook(unittest.TestCase):
    def test_the_cost_guard_is_not_the_publish_route_list(self) -> None:
        path = Path(__file__).resolve().parent.parent / ".claude" / "settings.json"
        settings = json.loads(path.read_text(encoding="utf-8"))

        registrations = settings["hooks"]["PreToolUse"]
        by_tool = {
            row["matcher"]: row["hooks"]
            for row in registrations
            if row["matcher"] in hook.COMMAND_TOOLS
        }
        self.assertEqual(set(by_tool), set(hook.COMMAND_TOOLS))
        self.assertNotIn("if", by_tool["Bash"][0])
        self.assertIn("tracker_publish_stub.py", by_tool["Bash"][0]["command"])
        for tool in ("PowerShell", "Monitor"):
            with self.subTest(tool=tool):
                self.assertNotIn("if", by_tool[tool][0])
                self.assertIn("tracker_publish_hook.py", by_tool[tool][0]["command"])
        for handlers in by_tool.values():
            self.assertEqual(len(handlers), 1)
            self.assertEqual(handlers[0]["timeout"], 30)

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
            [(row.field, row.text, row.origin, row.path) for row in result.publications],
            [("body", "Assigned body", "body-file", body.resolve())],
        )
        self.assertEqual(result.unreadable, ())


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

    def test_a_single_quoted_inline_variable_stays_literal(self) -> None:
        got = hook.extract("S='text'; gh issue comment 670 --body '$S/tail'")

        self.assertEqual(got.publications[0].text, "$S/tail")


class ACommandFilePregradeMatchesTheHook(unittest.TestCase):
    def test_publication_requires_a_resolved_path_exactly_for_body_files(self) -> None:
        resolved = Path.cwd().resolve() / "body.md"

        invalid = (
            ({"origin": "body-file"}, "path"),
            ({"origin": "inline", "path": resolved}, "path"),
            ({"origin": "unknown"}, "origin"),
            ({"origin": "body-file", "path": Path("body.md")}, "path"),
            ({"origin": "body-file", "path": str(resolved)}, "path"),
        )
        for keywords, field in invalid:
            with self.subTest(keywords=keywords):
                with self.assertRaisesRegex(ValueError, field):
                    hook.Publication("body", "text", **keywords)


class DeclaredLimitsHaveOneOwner(unittest.TestCase):
    def test_the_ratified_population_is_present_in_both_directions(self):
        """ADR 0287 moves the reading rows without changing their keys."""
        self.assertEqual(
            set(dict(hook.NOT_REACHED)),
            {
                'a GraphQL document assembled at run time is unreadable',
                'a file rewritten after the scan is graded on its earlier text',
                'a newly added API endpoint is refused until classified',
                'a program-formatted command is invisible',
                'a shell command assembled at run time is invisible',
                'a wrong non-publication entry silently passes',
                'an alias or function standing in for gh is invisible',
                'an argv list assembled in pieces is invisible',
                'assignment expansion is reconstructed and reaches only the same command',
                'the command-folder reader reaches literal absolute cd targets only',
                'which file an author meant is not established',
            },
        )


if __name__ == "__main__":
    unittest.main()
