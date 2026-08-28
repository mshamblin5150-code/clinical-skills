"""In-flight issue text carries dated, directional branch provenance."""

import contextlib
import io
import json
import unittest
from pathlib import Path
from unittest import mock

import tracker_branch_scope as scope
import tracker_merge_receipt as receipt


MARKER = (
    "> **Branch state:** `codex/ticket-290` at "
    "`abcdef0123456789abcdef0123456789abcdef01` is not on `main` as of "
    "`2026-08-20`.\n\n"
)
CITED_RECORD_MARKER = (
    "> **Cited record state:** `docs/adr/9999-not-on-main.md` is not on `main` "
    "as of `2026-08-27`.\n\n"
)


def main_url(path: str) -> str:
    return f"https://github.com/example/repo/blob/main/{path}"


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


class UnresolvedPathCitationsCarryDatedMainState(unittest.TestCase):
    def test_an_unresolved_absolute_citation_is_a_finding(self):
        result = scope.grade(
            comment_event(
                f"The record is [ADR 9999]({main_url('docs/adr/9999-not-on-main.md')}).",
                labels=("bug",),
            ),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)
        self.assertIn("unresolved path", result.report)
        self.assertNotIn("ADR 9999", result.report)

    def test_a_citation_inside_a_fence_is_only_a_mention(self):
        body = f"```markdown\n[example]({main_url('docs/adr/9999-not-on-main.md')})\n```"

        result = scope.grade(comment_event(body, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 0)

    def test_a_citation_inside_a_code_span_is_only_a_mention(self):
        body = f"Try `[example]({main_url('docs/adr/9999-not-on-main.md')})`."

        result = scope.grade(comment_event(body, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 0)

    def test_a_fragment_is_removed_before_a_live_path_is_resolved(self):
        body = main_url("tools/threshold_draft.py#L109")

        result = scope.grade(comment_event(body, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 0)

    def test_the_existing_branch_scope_satisfies_the_new_trigger(self):
        body = MARKER + main_url("docs/adr/9999-not-on-main.md")

        result = scope.grade(comment_event(body, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 0)

    def test_the_cited_record_scope_satisfies_the_new_trigger(self):
        body = CITED_RECORD_MARKER + main_url("docs/adr/9999-not-on-main.md")

        result = scope.grade(comment_event(body, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 0)

    def test_a_repo_relative_markdown_destination_is_a_finding(self):
        body = "See [the existing ADR](docs/adr/0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-rewritten-and-the-branch-scope-check-is-what-grades-it.md)."

        result = scope.grade(comment_event(body, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 1)
        self.assertIn("repo-relative Markdown link", result.report)
        self.assertNotIn("missing Branch state", result.report)

    def test_a_root_level_relative_markdown_destination_is_a_finding(self):
        result = scope.grade(
            comment_event("See [the README](README.md).", labels=("bug",)),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)
        self.assertIn("repo-relative Markdown link", result.report)

    def test_a_relative_destination_inside_code_is_only_a_mention(self):
        bodies = (
            "Try `[the README](README.md)`.",
            "```markdown\n[the README](README.md)\n```",
        )

        for body in bodies:
            with self.subTest(body=body):
                result = scope.grade(
                    comment_event(body, labels=("bug",)),
                    "issue_comment",
                )

                self.assertEqual(result.status, 0)

    def test_the_live_adr_0016_slug_typo_says_to_fix_the_slug(self):
        typo = (
            "docs/adr/0016-an-adr-number-is-claimed-when-it-is-handed-out-and-a-"
            "ratified-record-s-facts-may-be-corrected-in-place.md"
        )

        result = scope.grade(
            comment_event(main_url(typo), labels=("bug",)),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)
        self.assertIn("fix the slug", result.report)
        self.assertNotIn("missing Branch state", result.report)

    def test_a_genuinely_unmerged_path_still_demands_a_qualifier(self):
        result = scope.grade(
            comment_event(
                main_url("docs/adr/9999-not-on-main.md"),
                labels=("bug",),
            ),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)
        self.assertIn("missing Branch state", result.report)

    def test_each_absolute_main_url_spelling_is_resolved(self):
        path = "docs/adr/9999-not-on-main.md"
        urls = (
            f"https://github.com/example/repo/blob/main/{path}",
            f"https://github.com/example/repo/tree/main/{path}",
            f"https://github.com/example/repo/raw/main/{path}",
            f"https://raw.githubusercontent.com/example/repo/main/{path}",
        )

        for url in urls:
            with self.subTest(url=url):
                result = scope.grade(comment_event(url, labels=("bug",)), "issue_comment")

                self.assertEqual(result.status, 1)

    def test_a_live_tree_directory_resolves(self):
        url = "https://github.com/example/repo/tree/main/docs/adr"

        result = scope.grade(comment_event(url, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 0)

    def test_blob_and_raw_directory_urls_do_not_resolve(self):
        urls = (
            "https://github.com/example/repo/blob/main/docs/adr",
            "https://github.com/example/repo/raw/main/docs/adr",
            "https://raw.githubusercontent.com/example/repo/main/docs/adr",
        )

        for url in urls:
            with self.subTest(url=url):
                result = scope.grade(
                    comment_event(url, labels=("bug",)),
                    "issue_comment",
                )

                self.assertEqual(result.status, 1)
                self.assertIn("unresolved path", result.report)

    def test_the_path_specific_qualifier_names_the_unresolved_path(self):
        wrong_marker = (
            "> **Cited record state:** `docs/adr/9998-somewhere-else.md` is not "
            "on `main` as of `2026-08-27`.\n\n"
        )
        body = wrong_marker + main_url("docs/adr/9999-not-on-main.md")

        result = scope.grade(comment_event(body, labels=("bug",)), "issue_comment")

        self.assertEqual(result.status, 1)
        self.assertIn("missing Branch state", result.report)

    def test_qualifiers_do_not_create_a_trigger_around_a_live_path(self):
        live = main_url("tools/tracker_branch_scope.py")

        for marker in (MARKER, CITED_RECORD_MARKER):
            with self.subTest(marker=marker.splitlines()[0]):
                result = scope.grade(
                    comment_event(marker + live, labels=("bug",)),
                    "issue_comment",
                )

                self.assertEqual(result.status, 0)
                self.assertIn("no branch-state trigger", result.report)

    def test_adr_0048_does_not_trigger_the_unresolved_path_predicate(self):
        adr = (
            Path(__file__).resolve().parent.parent
            / "docs"
            / "adr"
            / "0048-a-tracker-citation-to-an-unmerged-path-is-dated-rather-than-"
            "rewritten-and-the-branch-scope-check-is-what-grades-it.md"
        ).read_text(encoding="utf-8")

        self.assertFalse(scope.cites_an_unresolved_path(adr))

    def test_default_branch_paths_are_read_from_remote_main_not_feature_head(self):
        completed = mock.Mock(stdout="tools/tracker_branch_scope.py\n")
        with mock.patch("subprocess.run", return_value=completed) as run:
            paths = scope._default_branch_paths()

        self.assertIn("tools/tracker_branch_scope.py", paths)
        self.assertEqual(
            ["git", "ls-tree", "-r", "--name-only", "origin/main"],
            run.call_args.args[0],
        )


class ExistingBranchScopeTriggersRemainIntact(unittest.TestCase):
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

    def test_a_merge_receipt_does_not_satisfy_an_unresolved_path_trigger(self):
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
        body += "\n\n" + main_url("docs/adr/9999-not-on-main.md")

        result = scope.grade(
            comment_event(body, labels=("bug", "in flight")),
            "issue_comment",
        )

        self.assertEqual(result.status, 1)
        self.assertIn("unresolved path", result.report)

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

    def test_text_mode_grades_raw_stdin(self):
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(io.StringIO()),
            mock.patch(
                "sys.stdin",
                io.StringIO(main_url("docs/adr/9999-not-on-main.md")),
            ),
        ):
            status = scope.main(["--text", "-"])

        self.assertEqual(status, 1)
        self.assertIn("unresolved path", output.getvalue())

    def test_text_mode_accepts_live_path_prose(self):
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            mock.patch(
                "sys.stdin",
                io.StringIO(main_url("tools/tracker_branch_scope.py")),
            ),
        ):
            status = scope.main(["--text", "-"])

        self.assertEqual(status, 0)


class PullRequestPublicationSurfacesAreGraded(unittest.TestCase):
    def event(self, event_name: str, body: str):
        pull_request = {
            "body": body,
            "html_url": "https://github.com/example/repo/pull/401",
        }
        document = {"pull_request": pull_request}
        if event_name == "pull_request_review":
            document["review"] = {
                "body": body,
                "html_url": "https://github.com/example/repo/pull/401#review-1",
            }
        elif event_name == "pull_request_review_comment":
            document["comment"] = {
                "body": body,
                "html_url": "https://github.com/example/repo/pull/401#discussion-1",
            }
        return document

    def test_each_pull_request_payload_fails_on_an_unresolved_path(self):
        body = main_url("docs/adr/9999-not-on-main.md")

        for event_name in (
            "pull_request_target",
            "pull_request_review",
            "pull_request_review_comment",
        ):
            with self.subTest(event_name=event_name):
                result = scope.grade(self.event(event_name, body), event_name)

                self.assertEqual(result.status, 1)
                self.assertIn("unresolved path", result.report)

    def test_a_pull_request_record_with_no_trigger_is_not_claimed(self):
        for event_name in (
            "pull_request_target",
            "pull_request_review",
            "pull_request_review_comment",
        ):
            with self.subTest(event_name=event_name):
                result = scope.grade(
                    self.event(event_name, "Ordinary pull request prose."),
                    event_name,
                )

                self.assertEqual(result.status, 0)


class DeclaredLimitsHaveOneOwner(unittest.TestCase):
    DOC = Path(__file__).resolve().parent.parent / "docs" / "agents" / "issue-tracker.md"

    def test_the_ruled_population_is_present_in_both_directions(self):
        self.assertEqual(
            set(dict(scope.NOT_REACHED)),
            {
                "publication precedes the check",
                "an advisory finding may go unread",
                "code formatting can hide a citation",
                "Branch state is a record-level proxy",
                "a bare record number has no path",
                "citation coordinates need file contents",
                "an undated assertion about a resolved path",
                "the qualifier forms cannot compose",
            },
        )

    def test_the_docs_point_at_the_object_and_copy_no_row(self):
        text = self.DOC.read_text(encoding="utf-8")

        self.assertIn("tracker_branch_scope.NOT_REACHED", text)
        for key, _reason in scope.NOT_REACHED:
            with self.subTest(key=key):
                self.assertNotIn(key, text)

    def test_the_module_points_back_at_the_document(self):
        self.assertIn("docs/agents/issue-tracker.md", scope.__doc__)

    def test_every_limit_carries_a_reason(self):
        for key, reason in scope.NOT_REACHED:
            with self.subTest(key=key):
                self.assertGreater(len(reason.split()), 8)


if __name__ == "__main__":
    unittest.main()
