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
import subprocess
import sys
import os
from unittest import mock

import artifact_lock_test_support  # noqa: F401
import tracker_publish_hook as hook
import tracker_bodies
import tracker_coordinates
import phi_scan
import tracker_publish_marker


_REAL_RECORD_RUN = hook.record_run
_RECORD_RUN_PATCHER = None


def setUpModule() -> None:
    global _RECORD_RUN_PATCHER
    _RECORD_RUN_PATCHER = mock.patch.object(hook, "record_run")
    _RECORD_RUN_PATCHER.start()


def tearDownModule() -> None:
    assert _RECORD_RUN_PATCHER is not None
    _RECORD_RUN_PATCHER.stop()


@contextlib.contextmanager
def working_directory(path: str):
    """Temporarily enter ``path`` on interpreters before ``contextlib.chdir``."""

    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def git(
    *args: str, cwd: Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=check,
    )


def fetched_records(
    number: int,
    labels: tuple[str, ...] = (),
    body: str = "invented record body",
) -> dict:
    """Return one complete invented GraphQL record keyed by its request number."""
    return {
        number: {
            "number": number,
            "state": "OPEN",
            "labels": {"nodes": [{"name": label} for label in labels]},
            "updatedAt": "2026-09-01T12:34:56Z",
            "body": body,
            "url": f"https://github.com/example/project/issues/{number}",
        }
    }


class RefreshDefaultBranchNamesTheRefItReads(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.writer = self.root / "writer"
        self.reader = self.root / "reader"

        git("init", "--bare", "--initial-branch=main", str(self.remote), cwd=self.root)
        git("clone", str(self.remote), str(self.writer), cwd=self.root)
        git("config", "user.name", "Test Writer", cwd=self.writer)
        git("config", "user.email", "writer@example.invalid", cwd=self.writer)
        self.commit_main("one\n", "initial")
        git("clone", str(self.remote), str(self.reader), cwd=self.root)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def commit_main(self, text: str, message: str, *, force: bool = False) -> str:
        (self.writer / "tracked.txt").write_text(text, encoding="utf-8")
        git("add", "--", "tracked.txt", cwd=self.writer)
        git("commit", "-m", message, cwd=self.writer)
        push_args = ("push", "--force", "origin", "HEAD:main") if force else (
            "push",
            "origin",
            "HEAD:main",
        )
        git(*push_args, cwd=self.writer)
        return git("rev-parse", "HEAD", cwd=self.writer).stdout.strip()

    def advance_main(self) -> str:
        return self.commit_main("two\n", "advance main")

    def test_a_clone_without_a_fetch_refspec_updates_origin_main(self) -> None:
        stale_tip = git("rev-parse", "origin/main", cwd=self.reader).stdout.strip()
        latest_tip = self.advance_main()
        git("fetch", "origin", "main", cwd=self.reader)
        self.assertEqual(
            git("rev-parse", "origin/main", cwd=self.reader).stdout.strip(),
            latest_tip,
        )
        git("config", "--unset-all", "remote.origin.fetch", cwd=self.reader)
        git("update-ref", "refs/remotes/origin/main", stale_tip, cwd=self.reader)

        plain_fetch = git("fetch", "origin", "main", cwd=self.reader)

        self.assertEqual(plain_fetch.returncode, 0)
        self.assertEqual(
            git("rev-parse", "origin/main", cwd=self.reader).stdout.strip(),
            stale_tip,
        )

        refreshed = hook.refresh_default_branch(repo=self.reader)

        self.assertTrue(refreshed)
        self.assertEqual(
            git("rev-parse", "origin/main", cwd=self.reader).stdout.strip(),
            latest_tip,
        )

    def test_a_force_pushed_main_replaces_the_rewritten_away_ref(self) -> None:
        rewritten_away_tip = self.advance_main()
        git("fetch", "origin", "main", cwd=self.reader)
        self.assertEqual(
            git("rev-parse", "origin/main", cwd=self.reader).stdout.strip(),
            rewritten_away_tip,
        )

        git("checkout", "--detach", "HEAD~1", cwd=self.writer)
        replacement_tip = self.commit_main("replacement\n", "rewrite main", force=True)

        unforced_fetch = git(
            "fetch",
            "--no-tags",
            "origin",
            "refs/heads/main:refs/remotes/origin/main",
            cwd=self.reader,
            check=False,
        )

        self.assertNotEqual(unforced_fetch.returncode, 0)
        self.assertEqual(
            git("rev-parse", "origin/main", cwd=self.reader).stdout.strip(),
            rewritten_away_tip,
        )

        refreshed = hook.refresh_default_branch(repo=self.reader)

        self.assertTrue(refreshed)
        self.assertEqual(
            git("rev-parse", "origin/main", cwd=self.reader).stdout.strip(),
            replacement_tip,
        )


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
    BODY_BY_KIND = {
        tracker_bodies.LOST_AT_DASH: "@-",
        tracker_bodies.EMPTY_BODY: " \n\t ",
        tracker_bodies.LITERAL_AT_PATH: "@body.md",
        tracker_bodies.DOUBLE_ENCODED: "before \u00e2\u20ac\u201d after",
        tracker_bodies.C0_CONTROL_CHARACTER: "word\bword",
        tracker_bodies.CARRIAGE_RETURN_FLANKED: "before\rafter",
        tracker_bodies.LITERAL_NEWLINE_ESCAPE: r"before\nafter",
        tracker_bodies.DOUBLED_PATH_SEPARATOR: r"open D:\\folder",
    }

    def test_every_declared_body_shape_is_refused(self) -> None:
        self.assertEqual(set(self.BODY_BY_KIND), set(tracker_bodies.KINDS))
        for kind, body in self.BODY_BY_KIND.items():
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(ValueError, kind):
                    hook.authorize_issue_body(body, "issue #596", issue_number=595)

    def test_a_map_body_without_a_producer_stamp_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "producer stamp"):
            hook.authorize_issue_body(
                "A complete tracker body.", "map", issue_number=596
            )

    def test_an_ordinary_non_map_body_is_accepted(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
        ):
            hook.authorize_issue_body(
                "A complete tracker body.", "issue #596", issue_number=595
            )

    def test_the_direct_writer_delegates_grading_only_to_analyze(self) -> None:
        index = phi_scan.build_index(set(), set())
        analysis = hook.Analysis((), "scanned body: 0 findings")
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "analyze", return_value=analysis) as analyze,
            mock.patch.object(
                hook.tracker_bodies, "grade", side_effect=AssertionError("direct call")
            ),
            mock.patch.object(
                hook.tracker_coordinates, "grade", side_effect=AssertionError("direct call")
            ),
            mock.patch.object(
                hook.tracker_measurements,
                "grade_current",
                side_effect=AssertionError("direct call"),
            ),
        ):
            report = hook.authorize_issue_body(
                "A complete tracker body.", "issue #595", issue_number=595
            )

        self.assertEqual(report, analysis.report)
        analyze.assert_called_once()
        publication = analyze.call_args.args[0]
        self.assertEqual((publication.field, publication.text), (
            "body", "A complete tracker body."
        ))

    def test_advice_is_returned_and_denial_refuses(self) -> None:
        index = phi_scan.build_index(set(), set())
        advised = hook.Analysis(
            (hook.Finding("phi:ssn", 1, "body", "advise"),),
            "advise: phi:ssn: 1 finding(s) in body",
        )
        denied = hook.Analysis(
            (hook.Finding("branch:repo-relative-link", 1, "body", "deny"),),
            "deny: branch:repo-relative-link: 1 finding(s) in body",
        )
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "analyze", side_effect=(advised, denied)),
        ):
            report = hook.authorize_issue_body("safe", "issue #595")
            with self.assertRaisesRegex(ValueError, "branch:repo-relative-link"):
                hook.authorize_issue_body("unsafe", "issue #595")

        self.assertIn("advise: phi:ssn", report)

    def test_an_absent_corpus_is_reported_without_refusing(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(
                hook, "current_index", return_value=(index, ("patient names",))
            ),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "analyze",
                return_value=hook.Analysis((), "scanned body: 0 findings"),
            ),
        ):
            report = hook.authorize_issue_body("safe", "issue #595")

        self.assertIn("PHI corpus layer incomplete", report)
        self.assertIn("patient names not available", report)

    def test_new_issue_title_and_body_are_both_graded_by_analyze(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "analyze",
                return_value=hook.Analysis((), "scanned field: 0 findings"),
            ) as analyze,
        ):
            hook.authorize_issue_body("body", "new issue", title="Map title")

        self.assertEqual(
            [call.args[0].field for call in analyze.call_args_list],
            ["body", "title"],
        )

    def test_issue_number_must_agree_with_the_record_context(self) -> None:
        with self.assertRaisesRegex(ValueError, "issue number and context disagree"):
            hook.authorize_issue_body(
                "body",
                "issue #595",
                issue_number=595,
                issue={"number": 596, "labels": []},
            )

    def test_canonical_docs_point_at_the_correspondence_objects(self) -> None:
        root = Path(__file__).resolve().parent.parent
        surfaces = (
            (root / "CLAUDE.md").read_text(encoding="utf-8"),
            (root / "docs" / "agents" / "issue-tracker.md").read_text(
                encoding="utf-8"
            ),
        )
        for surface in surfaces:
            with self.subTest(surface=surface[:40]):
                self.assertIn(
                    "tracker_publication_correspondence.WRITER_REACH", surface
                )
                self.assertIn(
                    "tracker_publication_correspondence.POSTURE_ROWS", surface
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

    def test_a_direct_substitution_is_refused_before_text_grading(self) -> None:
        payload = AnUnreadableBodyIsRefused.payload(
            "gh issue comment 670 --body \"$(printf '@-')\""
        )

        with mock.patch.object(hook, "current_index") as current_index:
            specific = hook.handle(payload)["hookSpecificOutput"]

        current_index.assert_not_called()
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unreadable body (expansion-exposed-inline)", specific["additionalContext"])
        self.assertNotIn("body:lost-at-dash", specific["additionalContext"])
        self.assertNotIn("0 findings", specific["additionalContext"])

    def test_an_unquoted_substitution_gets_the_field_specific_quoting_remedy(self) -> None:
        for command, field in (
            ("gh issue comment 670 --body $(printf body)", "body"),
            ("gh issue edit 670 --title $(printf title)", "title"),
        ):
            with self.subTest(field=field):
                specific = hook.handle(
                    AnUnreadableBodyIsRefused.payload(command)
                )["hookSpecificOutput"]

                self.assertEqual(specific["permissionDecision"], "deny")
                report = specific["additionalContext"]
                self.assertIn(
                    f"unreadable {field} (expansion-exposed-inline)", report
                )
                self.assertIn("must be requoted", report)
                if field == "title":
                    self.assertNotIn("--body-file", report)

    def test_a_title_refusal_names_single_quoting_not_a_body_file(self) -> None:
        response = hook.handle(
            AnUnreadableBodyIsRefused.payload(
                'gh issue edit 670 --title "Expanded $TITLE"'
            )
        )

        report = response["hookSpecificOutput"]["additionalContext"]
        self.assertIn("unreadable title (expansion-exposed-inline)", report)
        self.assertIn("single-quote", report)
        self.assertNotIn("--body-file", report)

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
    def test_every_absent_body_file_prints_the_one_missing_file_remedy(self) -> None:
        remedy = (
            "no file was at this path when the hook ran, which is before any "
            "part of this command runs, and a refused command runs none of its "
            "stages; if this command writes the file, write it in a separate "
            "command first, otherwise create it, then save the exact publication "
            "command and run `python tools/tracker_publish_hook.py --command-file "
            "<path>` before retrying"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            absent = (root / "body.md").as_posix()
            absolute_commands = {
                "redirect": (
                    f'echo hi > "{absent}" && '
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "heredoc": (
                    f'cat > "{absent}" <<EOF\nhi\nEOF\n'
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "python script": (
                    f'python tools/mk.py "{absent}" && '
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "copy": (
                    f'cp a.md "{absent}" && '
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "tee": (
                    f'echo hi | tee "{absent}" && '
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "python heredoc": (
                    "python - <<PY\n"
                    f"from pathlib import Path\nPath(r'{absent}').write_text('hi')\n"
                    "PY\n"
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "retry": f'gh issue comment 670 --body-file "{absent}"',
                "redirect to path suffix": (
                    f'echo hi > "{absent}.bak" && '
                    f'gh issue comment 670 --body-file "{absent}"'
                ),
                "high prefix and copy": (
                    f'echo "high " > "{absent}.x" && cp "{absent}.x" "{absent}" '
                    f'&& gh issue comment 670 --body-file "{absent}"'
                ),
            }

            for name, command in absolute_commands.items():
                with self.subTest(name=name):
                    specific = hook.handle(
                        AnUnreadableBodyIsRefused.payload(command)
                    )["hookSpecificOutput"]

                    self.assertEqual(specific["permissionDecision"], "deny")
                    self.assertIn(
                        "tracker pre-publish: NOT SCANNED -- unreadable body "
                        f"(missing-file); {remedy}",
                        specific["additionalContext"],
                    )

            relative = hook.handle(
                AnUnreadableBodyIsRefused.payload(
                    "python mk.py body.md && "
                    "gh issue comment 670 --body-file body.md"
                )
            )["hookSpecificOutput"]

        self.assertEqual(relative["permissionDecision"], "deny")
        self.assertIn(
            "tracker pre-publish: NOT SCANNED -- unreadable body (unrooted-path)",
            relative["additionalContext"],
        )

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
            [(row.field, row.text, row.origin) for row in result.publications],
            [
                ("title", "Ticket", "inline"),
                ("body", "First line\nSecond line", "inline heredoc"),
            ],
        )
        self.assertEqual(result.unreadable, ())


class PublishedFieldsAreGradedWithoutEchoingThem(unittest.TestCase):
    def test_a_tracker_body_cannot_switch_off_its_own_phi_shape_layer(self) -> None:
        body = "DOB: 01/02/2000\nSSN: 123-45-6789\nSeen 1/2/2026"
        index = phi_scan.build_index(set(), set())

        def phi_rows(text: str) -> list[tuple[str, int, str, str]]:
            analysis = hook.analyze(
                hook.Publication("body", text),
                index=index,
                issue=None,
                remote_fresh=True,
            )
            return [
                (row.rule, row.count, row.field, row.posture)
                for row in analysis.findings
                if row.rule.startswith("phi:")
            ]

        without_pragma = phi_rows(body)
        with_pragma = phi_rows(f"{phi_scan.SYNTHETIC_PRAGMA}\n{body}")

        self.assertTrue(without_pragma)
        self.assertEqual(without_pragma, with_pragma)

    def test_the_redaction_walk_covers_each_previously_silent_aperture(self) -> None:
        marker = "salted-redaction-marker-834"
        fixtures = {
            "phi:corpus-name": (marker, phi_scan.build_index({marker}, set()), None, None),
            "phi:corpus-date": (marker + " 09/09/2026", phi_scan.build_index(set(), {"09/09/2026"}), None, None),
            "phi:dob-with-date": (marker + " DOB: 01/02/2000", None, None, None),
            "phi:mrn-with-digits": (marker + " MRN: 12345", None, None, None),
            "phi:ssn": (marker + " 123-45-6789", None, None, None),
            "phi:phone": (marker + " 555-555-1212", None, None, None),
            "phi:us-short-date": (marker + " 1/2/2026", None, None, None),
            "body:lost-at-dash": ("@-", None, None, None),
            "body:empty-body": ("", None, None, None),
            "body:literal-at-path": ("@body.md", None, None, None),
            "body:double-encoded": (
                "before \u00e2\u20ac\u201d after", None, None, None
            ),
            "body:c0-control-character": (marker + "\bdamaged", None, None, None),
            "body:carriage-return-flanked": marker + "\rflanked",
            "body:literal-newline-escape": marker + r"\nliteral",
            "body:doubled-path-separator": marker + r" C:\\folder",
            tracker_coordinates.UNANCHORED: marker + " tools/example.py:12",
            "verdict:missing-discriminator": marker + "\n**Verdict:** HOLDS",
            hook.RETIRED_CITATION: (
                marker
                + " on #436's ruling: a correction below the advice is not a"
                " correction for anyone who acts on the advice."
            ),
            "branch:repo-relative-link": (marker + " [x](docs/x.md)", None, None, None),
            "branch:near-miss": (marker + " https://github.com/example/repo/blob/main/docs/adr/0083-not-the-real-slug.md", None, None, None),
            "branch:unresolved-path": (marker + " https://github.com/example/repo/blob/main/docs/adr/9999-not-on-main.md", None, None, None),
            "branch:self-declares-completion": ("Built on a branch. " + marker, None, None, None),
            "branch:in-flight": (marker + " ordinary", None, {"number": 834, "labels": ["in flight"]}, None),
            "branch:blockquote-missing": (
                "**Branch state:** `ticket-834` at `" + "a" * 40 + "` is not on `main` as of `2026-09-09`.\n" + marker,
                None, {"number": 834, "labels": ["in flight"]}, None,
            ),
            "branch:ancestry-refused": (
                "> **Branch state:** this text rests on `main` at `" + "a" * 40 + "` as of `2026-09-09`.\n" + marker,
                None, {"number": 834, "labels": ["in flight"]}, False,
            ),
        }
        fixtures = {
            kind: value if isinstance(value, tuple) else (value, None, None, None)
            for kind, value in fixtures.items()
        }
        triggered = set()
        for kind, (body, custom_index, issue, ancestry) in fixtures.items():
            with self.subTest(kind=kind):
                ancestry_patch = (
                    mock.patch.object(hook.tracker_branch_scope, "_main_ancestry", return_value=ancestry)
                    if ancestry is not None else contextlib.nullcontext()
                )
                with ancestry_patch:
                    result = hook.analyze(
                        hook.Publication("body", body),
                        index=custom_index or phi_scan.build_index(set(), set()),
                        issue=issue,
                        remote_fresh=True,
                    )
                rules = [finding.rule for finding in result.findings]
                self.assertIn(kind, rules)
                self.assertNotIn(marker, result.report)
                if kind in rules:
                    triggered.add(kind)
        report = hook.redaction_walk_report(triggered)
        print(report)
        self.assertEqual(set(fixtures), set(hook.REDACTION_WALK_KINDS))
        self.assertEqual(
            report,
            f"tracker redaction walk: {len(fixtures)}/{len(fixtures)} kinds triggered; unread: none",
        )

    def test_branch_posture_reads_the_typed_verdict_not_report_prose(self) -> None:
        typed = hook.tracker_branch_scope.Result(
            1,
            "display text with no machine-readable phrase",
            hook.tracker_branch_scope.Verdict(
                "branch:ancestry-refused", True, True
            ),
        )
        with mock.patch.object(
            hook.tracker_branch_scope, "grade_record", return_value=typed
        ):
            result = hook.analyze(
                hook.Publication("body", "ordinary text"),
                index=phi_scan.build_index(set(), set()),
                issue={"number": 834, "labels": ["in flight"]},
                remote_fresh=True,
            )

        self.assertIn(
            ("branch:ancestry-refused", "deny"),
            [(row.rule, row.posture) for row in result.findings],
        )

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

        for title in (
            "",
            "@-",
            "@body.md",
            "before \u00e2\u20ac\u201d after",
            r"before\nafter",
            r"open D:\\folder",
        ):
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

    def test_an_unanchored_coordinate_in_a_title_is_denied(self) -> None:
        result = hook.analyze(
            hook.Publication("title", "Moved to tools/example.py:12"),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

        coordinate_findings = [
            row for row in result.findings
            if row.rule == tracker_coordinates.UNANCHORED
        ]
        self.assertEqual(["deny"], [row.posture for row in coordinate_findings])
        self.assertIn(hook.COORDINATE_REMEDY, result.report)

    def test_title_record_keeps_graphql_identity_and_issue_container(self) -> None:
        context = hook.TrackerRecord(
            "old", "https://github.com/example/repo/issues/834", 834,
            ("in flight",), "issue", "body",
        )

        publication = hook.with_tracker_record(
            hook.Publication("title", "new"),
            route=("issue", "edit"),
            context=context,
        )

        self.assertEqual(publication.record.url, context.url)
        self.assertEqual(publication.record.container, "issue")
        self.assertEqual(publication.record.surface, "title")

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

    def test_a_commandless_monitor_payload_is_silent(self) -> None:
        with mock.patch.object(
            hook, "record_run"
        ) as write_marker:
            response = hook.handle(
                {
                    "hook_event_name": "PreToolUse",
                    "tool_name": "Monitor",
                    "tool_input": {"session_id": "monitor-1"},
                }
            )

        self.assertEqual(response, {})
        write_marker.assert_called_once_with()

    def test_a_read_only_command_records_the_hook_run(self) -> None:
        with mock.patch.object(
            hook, "record_run"
        ) as write_marker:
            response = hook.handle(self.payload("gh issue view 670"))

        self.assertEqual(response, {})
        write_marker.assert_called_once_with()

    def test_each_required_handle_path_writes_the_checkout_record(self) -> None:
        cases = {
            "read-only": self.payload("gh issue view 670"),
            "unmodeled-shell": {
                "hook_event_name": "PreToolUse",
                "tool_name": "PowerShell",
                "tool_input": {
                    "command": "gh issue comment 670 --body 'Ordinary body'"
                },
            },
            "analysis-failure": {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": 42},
            },
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, payload in cases.items():
                target = root / name / "record.json"
                with (
                    self.subTest(name=name),
                    mock.patch.object(
                        tracker_publish_marker, "marker_path", return_value=target
                    ),
                    mock.patch.object(hook, "record_run", _REAL_RECORD_RUN),
                ):
                    hook.handle(payload)

                record = json.loads(target.read_text(encoding="utf-8"))
                self.assertEqual(
                    record["version"], tracker_publish_marker.SCHEMA_VERSION
                )

    def test_an_unmodeled_shell_refuses_a_loose_publish_route(self) -> None:
        command = (
            "if (Test-Path 'body.md') { "
            "gh issue comment 1124 --body-file 'body.md' }"
        )
        with mock.patch.object(
            hook, "record_run"
        ) as write_marker:
            modeled = hook.handle(self.payload(command))
            unmodeled = hook.handle(
                {
                    "hook_event_name": "PreToolUse",
                    "tool_name": "PowerShell",
                    "tool_input": {"command": command},
                }
            )

        modeled_specific = modeled["hookSpecificOutput"]
        self.assertEqual(modeled_specific["permissionDecision"], "deny")
        self.assertIn("NOT SCANNED", modeled_specific["additionalContext"])
        self.assertIn("one top-level `gh`", modeled_specific["additionalContext"])
        self.assertIn("run that script from a file", modeled_specific["additionalContext"])
        specific = unmodeled["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertEqual(
            specific["permissionDecisionReason"], hook.UNSCANNED_REFUSAL
        )
        self.assertIn("unmodeled shell", specific["additionalContext"])
        self.assertIn("PowerShell", specific["additionalContext"])
        self.assertEqual(write_marker.call_count, 2)

    def test_each_unreproduced_shape_refuses_on_each_modeled_command_tool(self) -> None:
        commands = {
            "chained": (
                "gh issue comment 5 --body 'first' && "
                "gh issue comment 6 --body 'second'"
            ),
            "compound": "{ gh issue comment 5 --body 'text'; }",
            "nested": "sh -c \"gh issue comment 5 --body 'text'\"",
            "argv-list": (
                "python -c \"subprocess.run(['gh', 'issue', 'comment', '5', "
                "'--body-file', 'body.md'])\""
            ),
        }

        for tool_name in ("Bash", "Monitor"):
            for shape, command in commands.items():
                with self.subTest(tool=tool_name, shape=shape):
                    payload = self.payload(command)
                    payload["tool_name"] = tool_name
                    specific = hook.handle(payload)["hookSpecificOutput"]

                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertEqual(
                    specific["permissionDecisionReason"], hook.UNSCANNED_REFUSAL
                )
                self.assertIn("NOT SCANNED", specific["additionalContext"])

    def test_graphql_mutation_is_unclassified_on_each_modeled_command_tool(self) -> None:
        command = (
            "gh api graphql -f query='mutation { addComment(input: {}) "
            "{ clientMutationId } }'"
        )

        for tool_name in ("Bash", "Monitor"):
            with self.subTest(tool=tool_name):
                payload = self.payload(command)
                payload["tool_name"] = tool_name
                specific = hook.handle(payload)["hookSpecificOutput"]

                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertEqual(
                    specific["permissionDecisionReason"], hook.UNSCANNED_REFUSAL
                )
                self.assertIn("NOT SCANNED", specific["additionalContext"])
                self.assertIn("GraphQL mutation", specific["additionalContext"])
                self.assertIn("gh issue", specific["additionalContext"])
                self.assertIn("gh pr", specific["additionalContext"])

    def test_named_non_publications_are_untouched_on_modeled_tools(self) -> None:
        commands = (
            "gh api markdown -f text='render only'",
            "printf '%s' text | gh api markdown --input -",
            "gh api --method DELETE repos/example/project/git/refs/heads/topic",
            "gh api repos/example/project/issues/670/dependencies/blocked_by "
            "-f issue_id=671",
            "gh api graphql -f query='{ viewer { login } }'",
        )

        for tool_name in ("Bash", "Monitor"):
            for command in commands:
                with self.subTest(tool=tool_name, command=command):
                    payload = self.payload(command)
                    payload["tool_name"] = tool_name
                    self.assertEqual(hook.handle(payload), {})

    def test_graphql_mutation_in_a_same_command_variable_is_unclassified(self) -> None:
        command = (
            "QUERY='mutation { addComment(input: {}) { clientMutationId } }'; "
            'gh api graphql -f "query=$QUERY"'
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("GraphQL mutation", specific["additionalContext"])

    def test_selected_mutation_in_a_mixed_graphql_document_is_unclassified(self) -> None:
        command = (
            "gh api graphql -f operationName=Write "
            "-f query='query Read { viewer { login } } "
            "mutation Write { addComment(input: {}) { clientMutationId } }'"
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("GraphQL mutation", specific["additionalContext"])

    def test_selected_query_in_a_mixed_graphql_document_is_read_only(self) -> None:
        command = (
            "gh api graphql -f operationName=Read "
            "-f query='query Read { viewer { login } } "
            "mutation Write { addComment(input: {}) { clientMutationId } }'"
        )

        self.assertEqual(hook.handle(self.payload(command)), {})

    def test_later_repeated_graphql_query_field_decides_the_operation(self) -> None:
        command = (
            "gh api graphql -f query='query { viewer { login } }' "
            "-f query='mutation { addComment(input: {}) { clientMutationId } }'"
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("GraphQL mutation", specific["additionalContext"])

    def test_graphql_mutation_from_json_input_is_unclassified(self) -> None:
        request = json.dumps(
            {"query": "mutation { addComment(input: {}) { clientMutationId } }"}
        )
        command = (
            "gh api graphql --input - <<'JSON'\n"
            f"{request}\n"
            "JSON"
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("GraphQL mutation", specific["additionalContext"])

    def test_graphql_mutation_with_a_body_variable_is_unclassified(self) -> None:
        command = (
            "gh api graphql "
            "-f query='mutation($body: String!) { addComment(input: {}) "
            "{ clientMutationId } }' -f body='Publication text'"
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("GraphQL mutation", specific["additionalContext"])

    def test_unknown_write_endpoint_is_unclassified_on_modeled_tools(self) -> None:
        command = (
            "gh api repos/example/project/commits/abc/comments "
            "-f body='Commit comment'"
        )

        for tool_name in ("Bash", "Monitor"):
            with self.subTest(tool=tool_name):
                payload = self.payload(command)
                payload["tool_name"] = tool_name
                specific = hook.handle(payload)["hookSpecificOutput"]

                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertEqual(
                    specific["permissionDecisionReason"], hook.UNSCANNED_REFUSAL
                )
                self.assertIn("NOT SCANNED", specific["additionalContext"])
                self.assertIn("route table", specific["additionalContext"])
                self.assertIn("non-publication list", specific["additionalContext"])
                self.assertIn(
                    "unclassified API call", specific["additionalContext"]
                )
                self.assertNotIn("unreadable body", specific["additionalContext"])
                self.assertNotIn("resolved against", specific["additionalContext"])

    def test_unassigned_api_record_identifier_is_unclassified(self) -> None:
        command = (
            'gh api "repos/example/project/issues/comments/$CID" '
            "-f body='Comment edit'"
        )

        for tool_name in ("Bash", "Monitor"):
            with self.subTest(tool=tool_name):
                payload = self.payload(command)
                payload["tool_name"] = tool_name
                specific = hook.handle(payload)["hookSpecificOutput"]

                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertIn("NOT SCANNED", specific["additionalContext"])
                self.assertIn(
                    "type the literal identifier", specific["additionalContext"]
                )

    def test_unassigned_text_free_subresource_identifier_is_unclassified(self) -> None:
        command = (
            'gh api "repos/example/project/issues/$IID/labels" '
            "-f labels[]=bug"
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("type the literal identifier", specific["additionalContext"])

    def test_an_argv_list_publication_refuses_on_powershell(self) -> None:
        command = (
            "python -c \"subprocess.run(['gh', 'issue', 'comment', '5', "
            "'--body-file', 'body.md'])\""
        )
        payload = self.payload(command)
        payload["tool_name"] = "PowerShell"

        specific = hook.handle(payload)["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unmodeled shell", specific["additionalContext"])

    def test_the_nested_cd_fallback_uses_the_unreproduced_remedy(self) -> None:
        command = (
            "sh -c \"cd /tmp && gh issue comment 5 --body-file 'body.md'\""
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertIn("unreproduced publication", specific["additionalContext"])
        self.assertNotIn("repair and save", specific["additionalContext"])

    def test_a_flag_free_precise_call_does_not_hide_a_later_same_route_publish(self) -> None:
        command = "gh issue edit 5 --add-label bug && gh issue edit 6 --body 'text'"

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unreproduced publication", specific["additionalContext"])

    def test_a_read_only_precise_api_call_does_not_hide_a_later_api_publish(self) -> None:
        command = (
            "gh api graphql -f query='{viewer{login}}' && "
            "gh api repos/o/r/issues/6 -f body=x"
        )

        specific = hook.handle(self.payload(command))["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unreproduced publication", specific["additionalContext"])

    def test_loose_controls_that_do_not_publish_are_untouched(self) -> None:
        commands = (
            "gh issue edit 5 --add-label bug",
            "subprocess.run(['gh', 'issue', 'view', '5', '--json', 'body'])",
            "python -c \"print('no command')\"",
        )

        for tool_name in ("Bash", "Monitor", "PowerShell"):
            for command in commands:
                with self.subTest(tool=tool_name, command=command), mock.patch.object(
                    hook, "grade_command", return_value=None
                ):
                    payload = self.payload(command)
                    payload["tool_name"] = tool_name
                    self.assertEqual(hook.handle(payload), {})

    def test_powershell_still_refuses_graphql_query_fields(self) -> None:
        payload = self.payload("gh api graphql -f query='{viewer{login}}'")
        payload["tool_name"] = "PowerShell"

        specific = hook.handle(payload)["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unmodeled shell", specific["additionalContext"])

    def test_an_unmodeled_shell_leaves_read_only_gh_alone(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {
                "command": "if ($true) { gh issue view 1124 --json body }"
            },
        }

        self.assertEqual(hook.handle(payload), {})

    def test_any_unmodeled_roster_value_refuses_by_default(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "FutureShell",
            "tool_input": {"command": "gh issue comment 1124 --body 'text'"},
        }

        with mock.patch.dict(
            hook.COMMAND_TOOLS, {"FutureShell": "future-shell"}
        ):
            specific = hook.handle(payload)["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unmodeled shell", specific["additionalContext"])

    def test_an_unmodeled_shell_classifies_an_attached_short_body_flag(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {"command": "gh issue comment 1124 -bbody"},
        }

        specific = hook.handle(payload)["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unmodeled shell", specific["additionalContext"])

    def test_an_unmodeled_shell_checks_later_candidates_case_insensitively(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {
                "command": (
                    "gh issue view 1124 --json body; "
                    "GH issue comment 1124 --body text"
                )
            },
        }

        specific = hook.handle(payload)["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("unmodeled shell", specific["additionalContext"])

    def test_an_unmodeled_shell_classifies_a_newline_command_boundary(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "PowerShell",
            "tool_input": {
                "command": (
                    "Write-Output 'ready'\n"
                    "gh issue comment 1124 --body text"
                )
            },
        }

        specific = hook.handle(payload)["hookSpecificOutput"]

        self.assertEqual(specific["permissionDecision"], "deny")

    def test_monitor_uses_the_modeled_reader(self) -> None:
        payload = {
            "hook_event_name": "PreToolUse",
            "tool_name": "Monitor",
            "tool_input": {
                "command": "gh issue comment 1124 --body-file 'missing.md'"
            },
        }

        specific = hook.handle(payload)["hookSpecificOutput"]

        self.assertIn("unreadable body", specific["additionalContext"])
        self.assertNotIn("unmodeled shell", specific["additionalContext"])

    @staticmethod
    def body_commands(body: str) -> dict[tuple[str, ...], str]:
        inline = "'" + body + "'"
        return {
            ("issue", "create"): (
                f"gh issue create --title 'Ticket' --body {inline}"
            ),
            ("issue", "comment"): f"gh issue comment 595 --body {inline}",
            ("issue", "edit"): f"gh issue edit 595 --body {inline}",
            ("issue", "close"): f"gh issue close 595 --comment {inline}",
            ("pr", "create"): f"gh pr create --title 'Change' --body {inline}",
            ("pr", "comment"): f"gh pr comment 595 --body {inline}",
            ("pr", "edit"): f"gh pr edit 595 --body {inline}",
            ("pr", "review"): f"gh pr review 595 --approve --body {inline}",
            ("api",): (
                "gh api --method PATCH repos/example/project/issues/595 "
                f"-f body={inline}"
            ),
        }

    @staticmethod
    def body_file_commands(path: Path) -> dict[tuple[str, ...], str]:
        return {
            ("pr", "create"): f"gh pr create --title 'Change' --body-file \"{path}\"",
            ("pr", "edit"): f'gh pr edit 595 --body-file "{path}"',
            ("issue", "comment"): f'gh issue comment 595 --body-file "{path}"',
            ("pr", "comment"): f'gh pr comment 595 --body-file "{path}"',
            ("issue", "edit"): f'gh issue edit 595 --body-file "{path}"',
        }

    def test_an_unanchored_coordinate_is_denied_through_the_real_command_route(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(595),
            ),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload(
                    "gh issue comment 595 --body 'Moved to tools/example.py:12'"
                )
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual("deny", specific["permissionDecision"])
        self.assertIn(tracker_coordinates.UNANCHORED, specific["additionalContext"])
        self.assertIn("anchor", specific["additionalContext"])

    def test_an_unanchored_coordinate_is_denied_to_the_direct_writer(self) -> None:
        with self.assertRaisesRegex(ValueError, tracker_coordinates.UNANCHORED):
            hook.authorize_issue_body(
                "Moved to tools/example.py:12", "implementation map"
            )

    def test_every_declared_body_row_denies_every_body_bearing_route(self) -> None:
        bodies = DirectTrackerWritersCrossTheBodyGate.BODY_BY_KIND
        self.assertEqual(set(bodies), set(tracker_bodies.KINDS))
        index = phi_scan.build_index(set(), set())
        for kind, body in bodies.items():
            commands = self.body_commands(body)
            self.assertEqual(set(commands), set(hook.PUBLISH_ROUTES))
            for route, command in commands.items():
                with (
                    self.subTest(kind=kind, route=route),
                    mock.patch.object(
                        hook, "current_index", return_value=(index, ())
                    ),
                    mock.patch.object(
                        hook, "refresh_default_branch", return_value=True
                    ),
                    mock.patch.object(
                        hook,
                        "fetch_readback",
                        return_value=fetched_records(595),
                    ),
                    mock.patch.object(hook, "record_run"),
                ):
                    response = hook.handle(self.payload(command))

                specific = response["hookSpecificOutput"]
                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertIn(f"body:{kind}", specific["additionalContext"])

    def test_each_body_refusal_reports_its_remedy(self) -> None:
        bodies = DirectTrackerWritersCrossTheBodyGate.BODY_BY_KIND
        self.assertEqual(set(hook.BODY_REMEDIES), set(tracker_bodies.KINDS))
        for kind, body in bodies.items():
            with self.subTest(kind=kind):
                result = hook.analyze(
                    hook.Publication("body", body),
                    index=phi_scan.build_index(set(), set()),
                    issue=None,
                    remote_fresh=True,
                )

                self.assertIn(
                    f"remedy: {hook.BODY_REMEDIES[kind]}", result.report
                )

    def test_lost_body_remedies_name_the_absolute_body_file_route(self) -> None:
        for kind in (
            tracker_bodies.EMPTY_BODY,
            tracker_bodies.LOST_AT_DASH,
            tracker_bodies.LITERAL_AT_PATH,
        ):
            with self.subTest(kind=kind):
                remedy = hook.BODY_REMEDIES[kind]
                self.assertIn("body did not land", remedy)
                self.assertIn("absolute path", remedy)
                self.assertIn("--body-file", remedy)

    def test_double_encoded_remedy_keeps_damage_and_mentions_apart(self) -> None:
        remedy = hook.BODY_REMEDIES[tracker_bodies.DOUBLE_ENCODED]
        self.assertIn("cp1252", remedy)
        self.assertIn("UTF-8", remedy)
        self.assertIn("backticks", remedy)
        self.assertIn("genuine mention only", remedy)
        self.assertIn("hide damage", remedy)

    def test_empty_and_whitespace_only_body_files_are_refused(self) -> None:
        routes = {
            ("pr", "create"),
            ("pr", "edit"),
            ("issue", "comment"),
            ("pr", "comment"),
            ("issue", "edit"),
        }
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            body_file = Path(temporary) / "body.md"
            for body in ("", " \n\t "):
                body_file.write_text(body, encoding="utf-8")
                commands = self.body_file_commands(body_file)
                for route in routes:
                    with (
                        self.subTest(body=repr(body), route=route),
                        mock.patch.object(
                            hook, "current_index", return_value=(index, ())
                        ),
                        mock.patch.object(
                            hook, "refresh_default_branch", return_value=True
                        ),
                        mock.patch.object(
                            hook,
                            "fetch_readback",
                            return_value=fetched_records(595),
                        ),
                        mock.patch.object(hook, "record_run"),
                    ):
                        response = hook.handle(self.payload(commands[route]))

                    specific = response["hookSpecificOutput"]
                    self.assertEqual(specific["permissionDecision"], "deny")
                    self.assertIn("body:empty-body", specific["additionalContext"])

    def test_blank_issue_edit_with_a_filed_from_line_draws_both_denials(self) -> None:
        index = phi_scan.build_index(set(), set())
        current = (
            "**Filed from:** the clinician's request, 2026-09-11.\n\n"
            "Original body."
        )
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(595, body=current),
            ),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload("gh issue edit 595 --body ''")
            )

        report = response["hookSpecificOutput"]["additionalContext"]
        self.assertIn("deny: body:empty-body", report)
        self.assertIn("deny: filed-from:edit", report)

    def test_an_explicit_empty_pull_request_review_body_is_refused(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook, "fetch_readback", return_value=fetched_records(595)
            ),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload("gh pr review 595 --approve --body ''")
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("body:empty-body", specific["additionalContext"])
        self.assertIn("omit the --body flag", specific["additionalContext"])
        self.assertIn("if this is an approval", specific["additionalContext"])
        self.assertIn("otherwise supply", specific["additionalContext"])
        self.assertNotIn(
            "absolute path to --body-file", specific["additionalContext"]
        )

    def test_command_file_mode_refuses_an_empty_body(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "body.md"
            command_file = Path(temporary) / "publish.sh"
            body.write_text("", encoding="utf-8")
            command_file.write_text(
                f'gh issue comment 670 --body-file "{body.as_posix()}"',
                encoding="utf-8",
            )
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(
                    hook, "refresh_default_branch", return_value=True
                ),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                status = hook.main(["--command-file", str(command_file)])

        self.assertEqual(status, 1)

    def assert_commands_allowed(self, commands: tuple[str, ...]) -> None:
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(hook.handle(self.payload(command)), {})

    def test_parameterless_api_collection_reads_are_allowed(self) -> None:
        commands = (
            "gh api 'repos/example/project/issues?state=open'",
            "gh api 'repos/example/project/pulls?state=open'",
        )

        self.assert_commands_allowed(commands)

    def test_explicit_get_with_api_fields_is_allowed(self) -> None:
        commands = (
            "gh api --method GET repos/example/project/issues -f state=open",
            "gh api -X GET repos/example/project/issues -f state=open",
            "gh api --method GET repos/example/project/issues -f body=filter",
        )

        self.assert_commands_allowed(commands)

    def test_explicit_post_without_api_fields_uses_create_semantics(self) -> None:
        commands = (
            "gh api --method POST repos/example/project/issues",
            "gh api -X POST repos/example/project/issues",
        )

        for command in commands:
            with self.subTest(command=command):
                response = hook.handle(self.payload(command))
                specific = response["hookSpecificOutput"]
                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertIn("filed-from:create", specific["additionalContext"])

    def test_attached_api_fields_use_implicit_post_create_semantics(self) -> None:
        commands = (
            "gh api repos/example/project/issues -f=title='Ticket'",
            "gh api repos/example/project/issues -ftitle='Ticket'",
            "gh api repos/example/project/issues -F=title='Ticket'",
            "gh api repos/example/project/issues -Ftitle='Ticket'",
        )

        for command in commands:
            with self.subTest(command=command):
                response = hook.handle(self.payload(command))
                specific = response["hookSpecificOutput"]
                self.assertEqual(specific["permissionDecision"], "deny")
                self.assertIn("filed-from:create", specific["additionalContext"])

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
            mock.patch.object(hook, "record_run") as write_marker,
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

    def test_an_issue_create_without_a_filed_from_line_is_denied(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback") as fetch,
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload(
                    "gh issue create --title 'Ticket' "
                    "--body 'A body without its filing record.'"
                )
            )

        fetch.assert_not_called()
        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("filed-from:create", specific["additionalContext"])

    def test_a_title_only_issue_create_is_denied_as_an_empty_body(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback"),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload("gh issue create --title 'Ticket without a body'")
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("filed-from:create", specific["additionalContext"])

    def test_an_interactive_issue_create_is_denied_as_an_unreadable_body(self) -> None:
        response = hook.handle(self.payload("gh issue create"))

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("filed-from:create", specific["additionalContext"])

    def test_an_issue_create_accepts_the_line_at_each_fixed_position(self) -> None:
        index = phi_scan.build_index(set(), set())
        bodies = (
            "**Filed from:** the clinician's request, 2026-09-11.\n\nBody.",
            (
                "> **Cited record state:** `docs/adr/9999-unmerged.md` is not "
                "on `main` as of `2026-09-11`.\n"
                "\n"
                "**Filed from:** the architecture review, 2026-09-11.\n\nBody."
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index_number, body in enumerate(bodies):
                with self.subTest(index=index_number):
                    body_file = root / f"body-{index_number}.md"
                    body_file.write_text(body, encoding="utf-8")
                    with (
                        mock.patch.object(
                            hook, "current_index", return_value=(index, ())
                        ),
                        mock.patch.object(
                            hook, "refresh_default_branch", return_value=True
                        ),
                        mock.patch.object(hook, "fetch_readback") as fetch,
                        mock.patch.object(hook, "record_run"),
                    ):
                        response = hook.handle(
                            self.payload(
                                f"cd \"{root}\" && gh issue create --title 'Ticket' "
                                f'--body-file "{body_file.name}"'
                            )
                        )

                    fetch.assert_not_called()
                    specific = response["hookSpecificOutput"]
                    self.assertNotIn("permissionDecision", specific)
                    self.assertIn(
                        "filed-from: 0 fixed-line findings",
                        specific["additionalContext"],
                    )

    def test_a_measurement_under_a_quote_is_denied_with_remedy(self) -> None:
        body = "> quoted claim\n**Measured at:** " + "a" * 40
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback", return_value={}),
            mock.patch.object(
                hook.tracker_measurements, "current_head", return_value="a" * 40
            ),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body '" + body + "'")
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("measurement:inside-quote", specific["additionalContext"])
        self.assertIn(
            "remedy: add one blank line above the Measured at declaration",
            specific["additionalContext"],
        )

    def test_an_issue_edit_that_drops_the_existing_line_is_denied(self) -> None:
        index = phi_scan.build_index(set(), set())
        current = (
            "**Filed from:** the clinician's request, 2026-09-11.\n\n"
            "Original body."
        )
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(670, body=current),
            ),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload(
                    "gh issue edit 670 --body 'Replacement without the line.'"
                )
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("filed-from:edit", specific["additionalContext"])

    def test_an_issue_edit_that_alters_the_existing_line_is_denied(self) -> None:
        index = phi_scan.build_index(set(), set())
        current = "**Filed from:** the architecture review, 2026-09-11.\n\nOld."
        proposed = "**Filed from:** a later rewrite, 2026-09-12.\n\nNew."
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            body_file = root / "body.md"
            body_file.write_text(proposed, encoding="utf-8")
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(
                    hook, "refresh_default_branch", return_value=True
                ),
                mock.patch.object(
                    hook,
                    "fetch_readback",
                    return_value=fetched_records(670, body=current),
                ),
                mock.patch.object(hook, "record_run"),
            ):
                response = hook.handle(
                    self.payload(
                        f'cd "{root}" && gh issue edit 670 '
                        f'--body-file "{body_file.name}"'
                    )
                )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("filed-from:edit", specific["additionalContext"])

    def test_an_issue_edit_keeps_the_line_and_adds_a_correction_beneath_it(self) -> None:
        index = phi_scan.build_index(set(), set())
        filed_from = "**Filed from:** the clinician's request, 2026-09-11."
        current = filed_from + "\n\nOriginal body."
        proposed = (
            filed_from
            + "\n*Corrected 2026-09-12: filed during the build, not its review.*"
            + "\n\nReplacement body."
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            body_file = root / "body.md"
            body_file.write_text(proposed, encoding="utf-8")
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(
                    hook, "refresh_default_branch", return_value=True
                ),
                mock.patch.object(
                    hook,
                    "fetch_readback",
                    return_value=fetched_records(670, body=current),
                ),
                mock.patch.object(hook, "record_run"),
            ):
                response = hook.handle(
                    self.payload(
                        f'cd "{root}" && gh issue edit 670 '
                        f'--body-file "{body_file.name}"'
                    )
                )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn("filed-from: 0 fixed-line findings", specific["additionalContext"])

    def test_an_issue_edit_without_an_existing_line_is_not_refused_on_this_rule(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(
                hook,
                "fetch_readback",
                return_value=fetched_records(670, body="Original body."),
            ),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload("gh issue edit 670 --body 'Replacement body.'")
            )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn("filed-from: 0 fixed-line findings", specific["additionalContext"])

    def test_an_issue_edit_with_failed_readback_reports_not_graded(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback", side_effect=OSError("offline")),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload("gh issue edit 670 --body 'Replacement body.'")
            )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn(
            "filed-from: NOT GRADED; current issue body was not read",
            specific["additionalContext"],
        )

    def test_a_pull_request_create_is_not_graded_for_the_line(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback"),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload("gh pr create --title 'PR' --body 'Ordinary PR body.'")
            )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn("filed-from: NOT GRADED", specific["additionalContext"])

    def test_a_map_stamped_issue_body_is_not_graded_for_the_line(self) -> None:
        index = phi_scan.build_index(set(), set())
        commit = "a" * 40
        producer = "b" * 64
        body = (
            "<!-- implementation-map:v1:state:end -->\n\n"
            "## Snapshot\n"
            f"- producer: `tools/implementation_map.py sha256:{producer}`\n"
            f"- default-branch commit: `{commit}`\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            body_file = root / "map.md"
            body_file.write_text(body, encoding="utf-8")
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(
                    hook, "refresh_default_branch", return_value=True
                ),
                mock.patch.object(hook, "fetch_readback"),
                mock.patch.object(hook, "record_run"),
                mock.patch(
                    "implementation_map.producer_identity", return_value=producer
                ),
            ):
                response = hook.handle(
                    self.payload(
                        f"cd \"{root}\" && gh issue create --title 'Map' "
                        f'--body-file "{body_file.name}"'
                    )
                )

        specific = response["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", specific)
        self.assertIn("implementation map producer stamp", specific["additionalContext"])

    def test_an_api_issue_create_without_the_line_is_denied(self) -> None:
        index = phi_scan.build_index(set(), set())
        with (
            mock.patch.object(hook, "current_index", return_value=(index, ())),
            mock.patch.object(hook, "refresh_default_branch", return_value=True),
            mock.patch.object(hook, "fetch_readback"),
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload(
                    "gh api --method POST repos/example/project/issues "
                    "-f title='Ticket' -f body='Missing filing record.'"
                )
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("filed-from:create", specific["additionalContext"])

    def test_command_file_mode_grades_the_filed_from_route(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "body.md"
            command_file = Path(temporary) / "publish.sh"
            body.write_text("Ordinary body.", encoding="utf-8")
            command_file.write_text(
                "gh issue create --title 'Ticket' "
                f'--body-file "{body.as_posix()}"',
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(
                    hook, "refresh_default_branch", return_value=True
                ),
                contextlib.redirect_stdout(stdout),
            ):
                status = hook.main(["--command-file", str(command_file)])

        self.assertEqual(status, 1)
        self.assertIn("filed-from:create", stdout.getvalue())
        self.assertNotIn("filed-from: NOT GRADED", stdout.getvalue())

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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
        ):
            response = hook.handle(
                self.payload(
                    "gh issue edit 723 --title 'damaged\btitle' "
                    "--body 'damaged\bbody'"
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
        self.assertIn("--command-file <path>", unreadable_report)
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
            mock.patch.object(
                hook, "record_run"
            ) as write_marker,
        ):
            response = hook.handle(
                self.payload("gh issue comment 670 --body 'Ordinary body'")
            )

        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn("analysis failed (RuntimeError)", specific["additionalContext"])
        self.assertNotIn("Unreadable body", specific["additionalContext"])
        write_marker.assert_called_once_with()

    def test_a_failed_marker_write_does_not_change_the_hook_response(self) -> None:
        payload = self.payload("gh issue view 670")
        with (
            mock.patch.object(hook, "record_run", _REAL_RECORD_RUN),
            mock.patch.object(
                tracker_publish_marker,
                "write_marker",
                side_effect=OSError("read only"),
            ),
        ):
            response = hook.handle(payload)

        self.assertEqual(response, {})

    def test_the_hook_marker_is_dated_and_contains_no_tracker_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            runs = Path(temporary) / "runs"
            marker = tracker_publish_marker.write_marker(runs_root=runs)

            document = json.loads(marker.read_text(encoding="utf-8"))

        self.assertEqual(set(document), {"version", "ran_on"})
        self.assertEqual(document["version"], 2)
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

    def test_the_full_entry_point_records_before_payload_parsing(self) -> None:
        stdin = io.StringIO("{not-json")
        stdout = io.StringIO()
        with (
            mock.patch.object(sys, "stdin", stdin),
            mock.patch.object(
                hook, "record_run"
            ) as write_marker,
            contextlib.redirect_stdout(stdout),
        ):
            status = hook.main([])

        self.assertEqual(status, 0)
        write_marker.assert_called_once_with()
        self.assertIn(
            "HOOK FAILURE",
            json.loads(stdout.getvalue())["hookSpecificOutput"]["additionalContext"],
        )

    def test_the_command_file_mode_fulfills_the_unreadable_remedy(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            body = Path(temporary) / "body.md"
            command_file = Path(temporary) / "publish.sh"
            body.write_text("[record](docs/adr/0083.md)", encoding="utf-8")
            command_file.write_text(
                f'gh issue comment 670 --body-file "{body.as_posix()}"',
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(hook, "refresh_default_branch", return_value=True),
                contextlib.redirect_stdout(stdout),
            ):
                status = hook.main(["--command-file", str(command_file)])

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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
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
            mock.patch.object(hook, "record_run"),
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
            "errors": [{
                "type": "NOT_FOUND",
                "path": ["repository", "record_18"],
                "message": "Could not resolve record 18",
            }],
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

    def test_forbidden_null_alias_is_not_misreported_as_absent(self) -> None:
        payload = {
            "data": {"repository": {"record_17": None}},
            "errors": [{
                "type": "FORBIDDEN",
                "path": ["repository", "record_17"],
                "message": "Resource not accessible",
            }],
        }
        completed = mock.Mock(returncode=1, stdout=json.dumps(payload), stderr="error")

        with mock.patch.object(hook.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(ValueError, "FORBIDDEN"):
                hook.fetch_readback(frozenset({17}))

    def test_nested_not_found_is_not_misreported_as_an_absent_record(self) -> None:
        payload = {
            "data": {"repository": {"record_17": {"number": 17, "labels": None}}},
            "errors": [{
                "type": "NOT_FOUND",
                "path": ["repository", "record_17", "labels"],
                "message": "Labels could not be read",
            }],
        }
        completed = mock.Mock(returncode=1, stdout=json.dumps(payload), stderr="error")

        with mock.patch.object(hook.subprocess, "run", return_value=completed):
            with self.assertRaisesRegex(ValueError, "labels"):
                hook.fetch_readback(frozenset({17}))


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


class DeclaredLimitsHaveOneOwner(unittest.TestCase):
    def test_the_ratified_population_is_present_in_both_directions(self):
        """Two rulings own this object, and each row belongs to exactly one.

        ADR 0089 ratified the four bypass rows -- ways the hook never runs at
        all. ADR 0096 added the three that describe what a run it *did* perform
        does not establish, and ADR 0104 adds the failed-readback path, on the
        rule this object already carried: a limit lives here rather than in the
        docstring or ``CLAUDE.md``. ADR 0109 adds the AAR paraphrase ceiling.
        #999 ruling 5 adds the non-canonical-origin boundary. ADR 0191 ruling 8
        adds the retired-citation row's one-pairing ceiling. ADR 0234 adds the
        two non-publication-list floors and the runtime GraphQL-document limit.
        ADR 0244 adds the limit on establishing which file an author meant.
        ADR 0246 adds the per-checkout marker's five notice boundaries.
        """
        self.assertEqual(
            set(dict(hook.NOT_REACHED)),
            {
                "the GitHub web UI bypasses the hook",
                "disabled or overridden hooks bypass the check",
                "retained pre-edit revisions remain readable",
                "workspace trust can silently suppress registration",
                "a commit outside a session does not run the marker",
                "the record belongs to the checkout whose hook module ran",
                "disabled or overridden hooks leave the record aging",
                "the marker is not a publish-time guarantee",
                "moving or renaming a checkout changes its identity",
                "a file rewritten after the scan is graded on its earlier text",
                "assignment expansion is reconstructed and reaches only the same command",
                "no route rule covers the cause side of escape collapse",
                "the refusing hook covers one of two publishers",
                "a failed tracker readback leaves the publication context-blind",
                "the fetched origin can be a non-canonical repository",
                "an AAR paraphrase passes the quotation gate",
                "the command-folder reader reaches literal absolute cd targets only",
                "a stock discriminator clause can satisfy the verdict form check",
                "the retired-citation row reaches one literal pairing",
                "a shell command assembled at run time is invisible",
                "a program-formatted command is invisible",
                "an argv list assembled in pieces is invisible",
                "an alias or function standing in for gh is invisible",
                "a newly added API endpoint is refused until classified",
                "a wrong non-publication entry silently passes",
                "a GraphQL document assembled at run time is unreadable",
                "which file an author meant is not established",
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

    def test_a_single_quoted_inline_variable_stays_literal(self) -> None:
        got = hook.extract("S='text'; gh issue comment 670 --body '$S/tail'")

        self.assertEqual(got.publications[0].text, "$S/tail")


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
        return hook.Publication("body", text, "body-file", body.resolve())

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


class ACommandFilePregradeMatchesTheHook(unittest.TestCase):
    @staticmethod
    def payload(command: str) -> dict:
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }

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

    def test_an_aar_copy_is_denied_with_the_same_population_line(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            run = Path(temporary) / "run"
            source = run / "working.md"
            body = run / "aar" / "publications" / "ticket.md"
            command_file = run / "publish.sh"
            body.parent.mkdir(parents=True)
            material = "A deliberately distinctive private working sentence " * 4
            source.write_text(material, encoding="utf-8")
            body.write_text(material[: hook.AAR_QUOTE_SPAN_CHARS], encoding="utf-8")
            command = f'gh issue comment 670 --body-file "{body.as_posix()}"'
            command_file.write_text(command, encoding="utf-8")
            stdout = io.StringIO()
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(hook, "refresh_default_branch", return_value=True),
                mock.patch.object(hook, "fetch_readback", return_value=fetched_records(670)),
                mock.patch.object(hook, "record_run"),
                contextlib.redirect_stdout(stdout),
            ):
                status = hook.main(["--command-file", str(command_file)])
                response = hook.handle(self.payload(command))

        expected = "AAR quotation gate: 1 copied private-run span(s) across 1 AAR publication(s)"
        self.assertEqual(status, 1)
        self.assertIn(expected, stdout.getvalue())
        specific = response["hookSpecificOutput"]
        self.assertEqual(specific["permissionDecision"], "deny")
        self.assertIn(expected, specific["additionalContext"])

    def test_an_ordinary_body_reports_the_same_not_applicable_population(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            body = root / "ticket.md"
            command_file = root / "publish.sh"
            body.write_text("An ordinary tracker body.", encoding="utf-8")
            command = f'gh issue comment 670 --body-file "{body.as_posix()}"'
            command_file.write_text(command, encoding="utf-8")
            stdout = io.StringIO()
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(hook, "refresh_default_branch", return_value=True),
                mock.patch.object(hook, "fetch_readback", return_value=fetched_records(670)),
                mock.patch.object(hook, "record_run"),
                contextlib.redirect_stdout(stdout),
            ):
                status = hook.main(["--command-file", str(command_file)])
                response = hook.handle(self.payload(command))

        expected = (
            "AAR quotation gate: not applicable -- no publication under "
            "aar/publications/"
        )
        self.assertEqual(status, 0)
        self.assertIn(expected, stdout.getvalue())
        self.assertIn(expected, response["hookSpecificOutput"]["additionalContext"])

    def test_a_typo_or_empty_command_file_is_not_scanned(self) -> None:
        for command in ("gh issue creat --body 'text'", ""):
            with self.subTest(command=command):
                with tempfile.TemporaryDirectory() as temporary:
                    command_file = Path(temporary) / "publish.sh"
                    command_file.write_text(command, encoding="utf-8")
                    stdout = io.StringIO()
                    with contextlib.redirect_stdout(stdout):
                        status = hook.main(["--command-file", str(command_file)])

                self.assertEqual(status, 2)
                self.assertEqual(
                    stdout.getvalue().strip(),
                    "tracker pre-publish: NOT SCANNED -- no publication route "
                    "recognized in the command file",
                )

    def test_a_recognized_route_without_publication_fields_is_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            command_file = Path(temporary) / "publish.sh"
            command_file.write_text("gh issue comment 670", encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = hook.main(["--command-file", str(command_file)])

        self.assertEqual(status, 2)
        self.assertIn("no publication fields recognized", stdout.getvalue())
        self.assertNotIn("no publication route recognized", stdout.getvalue())
        self.assertEqual(hook.handle(self.payload("gh issue comment 670")), {})

    def test_an_unrooted_body_file_is_not_scanned_on_both_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            command_file = Path(temporary) / "publish.sh"
            command = "gh issue comment 670 --body-file relative.md"
            command_file.write_text(command, encoding="utf-8")
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = hook.main(["--command-file", str(command_file)])
            response = hook.handle(self.payload(command))

        self.assertEqual(status, 2)
        self.assertIn("(unrooted-path)", stdout.getvalue())
        self.assertIn(
            "(unrooted-path)",
            response["hookSpecificOutput"]["additionalContext"],
        )

    def test_issue_create_without_filed_from_is_denied_on_both_routes(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            body = root / "ticket.md"
            command_file = root / "publish.sh"
            body.write_text("No filing record.", encoding="utf-8")
            command = (
                "gh issue create --title 'Ticket' "
                f'--body-file "{body.as_posix()}"'
            )
            command_file.write_text(command, encoding="utf-8")
            stdout = io.StringIO()
            with (
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(hook, "refresh_default_branch", return_value=True),
                mock.patch.object(hook, "record_run"),
                contextlib.redirect_stdout(stdout),
            ):
                status = hook.main(["--command-file", str(command_file)])
                response = hook.handle(self.payload(command))

        self.assertEqual(status, 1)
        self.assertIn("filed-from:create", stdout.getvalue())
        self.assertEqual(
            response["hookSpecificOutput"]["permissionDecision"], "deny"
        )
        self.assertIn(
            "filed-from:create",
            response["hookSpecificOutput"]["additionalContext"],
        )

    def test_a_pregrade_does_not_touch_the_hook_marker(self) -> None:
        index = phi_scan.build_index(set(), set())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            command_file = root / "publish.sh"
            command_file.write_text(
                "gh issue comment 670 --body 'Ordinary body.'", encoding="utf-8"
            )
            with (
                mock.patch.object(
                    hook, "record_run"
                ) as write_marker,
                mock.patch.object(hook, "current_index", return_value=(index, ())),
                mock.patch.object(hook, "refresh_default_branch", return_value=True),
                mock.patch.object(hook, "fetch_readback", return_value=fetched_records(670)),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                status = hook.main(["--command-file", str(command_file)])

            self.assertEqual(status, 0)
            write_marker.assert_not_called()

    def test_text_is_retired_and_no_unreadable_remedy_points_to_it(self) -> None:
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = hook.main(["--text", "body.md"])

        self.assertEqual(status, 2)
        self.assertIn("unsupported arguments", stderr.getvalue())
        self.assertNotIn("--text", "\n".join(hook.UNREADABLE_REMEDIES.values()))


class TheRetiredCorrectionCitationIsReported(unittest.TestCase):
    """ADR 0191 ruling 8, over the shapes the tracker actually published.

    The controls are written here rather than read out of a committed file on
    purpose: every live member of the population is what #934's repair removes,
    so a test keyed on one would go red when the repair lands. Their wording is
    copied from the records the 2026-09-12 harvest measured.
    """

    FOOTER = (
        "*Corrected 2026-09-06 by the tracker sweep. Edited in place rather than"
        " commented, on [#436](https://github.com/mshamblin5150-code/"
        "clinical-skills/issues/436)'s ruling: a correction below the advice is"
        " not a correction for anyone who acts on the advice.*"
    )

    def analysis(self, text: str) -> hook.Analysis:
        return hook.analyze(
            hook.Publication("body", text),
            index=phi_scan.build_index(set(), set()),
            issue=None,
            remote_fresh=True,
        )

    def test_a_published_footer_is_reported_and_never_denied(self) -> None:
        result = self.analysis(self.FOOTER)

        self.assertIn(
            (hook.RETIRED_CITATION, 1, "body", "advise"),
            [(row.rule, row.count, row.field, row.posture) for row in result.findings],
        )
        self.assertEqual(
            [], [row for row in result.findings if row.posture == "deny"]
        )

    def test_each_reference_form_counts_on_its_own(self) -> None:
        """One control per branch: the published footer carries both at once.

        ``self.FOOTER`` is a Markdown link whose text is ``#436`` and whose
        target ends ``issues/436``, so it satisfies either alternative and
        discriminates neither. These do not.
        """
        forms = {
            "bare": "On #436's ruling, no correction below the advice reaches anyone.",
            "url only": (
                "On https://github.com/mshamblin5150-code/clinical-skills/issues/436"
                ", no correction below the advice reaches anyone."
            ),
        }
        for label, text in forms.items():
            with self.subTest(form=label):
                self.assertEqual(
                    [
                        row.count
                        for row in self.analysis(text).findings
                        if row.rule == hook.RETIRED_CITATION
                    ],
                    [1],
                )

    def test_a_longer_number_starting_436_is_not_the_retired_ticket(self) -> None:
        """The word boundary is the narrowing; #4360 is a different ticket."""
        text = "On #4360's ruling, no correction below the advice reaches anyone."

        self.assertEqual(hook.retired_citation_paragraphs(text), 0)

    def test_a_sentence_initial_wording_is_read(self) -> None:
        """``test_allergy_reaction``'s case-sensitive NUMERAL, one module over.

        A figure opening a sentence went silently ungraded there. Here it is the
        rule opening one, and the defect would be latent rather than live: no
        published member happens to capitalize it.
        """
        text = "On #436's ruling. Below the advice is not a correction."

        self.assertEqual(hook.retired_citation_paragraphs(text), 1)

    def test_each_wording_is_read_on_its_own(self) -> None:
        """One control per phrase, because two in one control pass on either."""
        wordings = {
            "below the advice": "a correction below the advice is not a correction",
            "acts on the advice": "no correction for anyone who acts on the advice",
            "acting on the advice": "no correction for anyone acting on the advice",
        }
        self.assertEqual(set(wordings), set(hook.CORRECT_IN_PLACE_PHRASES))
        for phrase, sentence in wordings.items():
            with self.subTest(phrase=phrase):
                text = f"On #436's ruling, {sentence}."
                self.assertEqual(hook.retired_citation_paragraphs(text), 1)

    def test_the_rule_stated_without_the_citation_is_left_alone(self) -> None:
        """#781's comment reasons the rule out and cites nobody; it is not a finding."""
        text = (
            "A correction one screen below advice is not a correction for anyone"
            " who acts on the advice."
        )

        self.assertEqual(
            [],
            [
                row
                for row in self.analysis(text).findings
                if row.rule == hook.RETIRED_CITATION
            ],
        )

    def test_the_citation_in_another_paragraph_is_left_alone(self) -> None:
        """A record about #436's real subject beside an unrelated correction."""
        text = (
            "The 160-char window in #436 cut records mid-word.\n\n"
            "A correction below the advice reaches nobody who acted on it."
        )

        self.assertEqual(hook.retired_citation_paragraphs(text), 0)

    def test_each_paragraph_is_counted(self) -> None:
        self.assertEqual(
            hook.retired_citation_paragraphs(self.FOOTER + "\n\n" + self.FOOTER), 2
        )

    def test_the_report_names_the_remedy_and_echoes_no_text(self) -> None:
        marker = "salted-retired-citation-marker-934"
        report = self.analysis(marker + " " + self.FOOTER).report

        self.assertIn(f"advise: {hook.RETIRED_CITATION}", report)
        self.assertIn("ADR 0016", report)
        self.assertIn("ADR 0191", report)
        self.assertNotIn(marker, report)

    def test_a_deliberate_quotation_is_reported_too_and_that_is_declared(self) -> None:
        """The mention-versus-use limit is why the row advises rather than denies."""
        quoting = (
            "The sentence, published verbatim across the tracker:\n\n"
            "> *on #436's ruling: a correction below the advice is not a"
            " correction for anyone who acts on the advice*"
        )

        self.assertEqual(hook.retired_citation_paragraphs(quoting), 1)
        self.assertTrue(
            any(
                "retired-citation row reaches one literal pairing" in subject
                for subject, _reason in hook.NOT_REACHED
            )
        )


if __name__ == "__main__":
    unittest.main()
